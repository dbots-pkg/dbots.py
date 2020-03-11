import asyncio
import atexit
import logging
from .http import HTTPClient, HTTPResponse
from .eventhandler import EventHandler
from .client_filler import ClientFiller
from .service import Service
from .errors import APIKeyException

log = logging.getLogger(__name__)

class AsyncLoop:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        while True:
            await asyncio.sleep(self._timeout)
            await self._callback()

    def cancel(self):
        self._task.cancel()

def _ensure_coro(func):
    if not asyncio.iscoroutinefunction(func):
        func = asyncio.coroutine(func)
    return func

class Poster(EventHandler):
    """
    A class that posts server count to listing sites.

    Parameters
    -----------
    client_id: :class:`str`
        The client ID used for posting to a service.
    server_count: function or `coroutine`
        The function to use when retrieving the amount of servers.
    user_count: function or `coroutine`
        The function to use when retrieving the amount of users.
    voice_connections: function or `coroutine`
        The function to use when retrieving the amount of voice connections.
    on_custom_post: Optional[function or `coroutine`]
        The function to use when posting to a `custom` service.
        This function will be used with the named parameters being
        `server_count`, `user_count` and `voice_connections`.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        `asyncio.get_event_loop()`.
    sharding: Optional[:class:`bool`]
        Whether or not to use sharding values.
    shard_count: Optional[:class:`int`]
        The amount of shards the client has.
    shard_id: Optional[:class:`int`]
        The shard ID the poster us posting for.
    proxy: Optional[:class:`str`]
        Proxy URL.
    proxy_auth: Optional[:class:`aiohttp.BasicAuth`]
        An object that represents proxy HTTP Basic Authorization.
    api_keys: Optional[:class:`dict`]
        A dictionary of API keys with the key being service keys and values being tokens.
    """

    def __init__(
        self, client_id, server_count, user_count,
        voice_connections, on_custom_post = None, **options
    ):
        super().__init__(loop = options.pop('loop', None))

        self._loop = None
        self._client_id = client_id
        if options.pop('sharding', True):
            self._shard_id = options.pop('shard_id', None)
            self._shard_count = options.pop('shard_count', None)
        else:
            self._shard_id = None
            self._shard_count = None

        proxy = options.pop('proxy', None)
        proxy_auth = options.pop('proxy_auth', None)
        self.http = HTTPClient(proxy = proxy, proxy_auth = proxy_auth)
        self.api_keys = options.pop('api_keys', {})

        setattr(self, 'server_count', _ensure_coro(server_count))
        setattr(self, 'user_count', _ensure_coro(user_count))
        setattr(self, 'voice_connections', _ensure_coro(voice_connections))
        if on_custom_post:
            setattr(self, 'on_custom_post', _ensure_coro(on_custom_post))
        atexit.register(self.kill_loop)

    def __repr__(self):
        attrs = [
            ('client_id', self.client_id),
            ('shard_id', self.shard_id),
            ('shard_count', self.shard_count),
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))
    
    # property fill-ins
    
    @property
    def client_id(self) -> str or None:
        """The client ID of the poster."""
        return self._client_id
    
    @property
    def shard_id(self) -> int or None:
        """The shard ID of the poster."""
        return self._shard_id
    
    @property
    def shard_count(self) -> int or None:
        """The shard count of the poster."""
        return self._shard_count

    # api key management
    
    def set_key(self, service: str, key: str) -> str:
        """
        Sets an API key.

        Parameters
        -----------
        service: :class:`str`
            The service key to set.
        key: :class:`str`
            The API key to use.
        """
        self.api_keys[service] = key
        return key

    def get_key(self, service: str) -> str:
        """
        Gets an API key.

        Parameters
        -----------
        service: :class:`str`
            The service key to get.
        """
        return self.api_keys[service]

    def remove_key(self, service: str) -> str:
        """
        Removes an API key.

        Parameters
        -----------
        service: :class:`str`
            The service key to remove.
        """
        key = self.api_keys[service]
        del self.api_keys[service]
        return key
    
    # loop management
    
    def start_loop(self, interval = 1800) -> AsyncLoop:
        """
        Creates a loop that posts to all services every `n` seconds.

        Parameters
        -----------
        interval: Optional[:class:`int`]
            The amount of time (in seconds) to post to all services again.
        """
        self.kill_loop()
        self._loop = AsyncLoop(interval, self.__on_loop)
        log.debug('Started loop %s', interval)
        return self._loop
    
    def kill_loop(self):
        """Cancels the current posting loop."""
        if self._loop:
            log.debug('Ending loop')
            self._loop.cancel()
            self._loop = None
    
    async def __on_loop(self):
        log.debug('Loop ran')
        try:
            responses = await self.post()
            log.debug('Autoposting %s services, %s', len(responses), responses)
            self.dispatch('auto_post', responses)
            return responses
        except Exception as error:
            log.debug('Autoposting failed, %s', error)
            self.dispatch('auto_post_fail', error)
            raise error

    # post management

    async def post(self, service = None) -> HTTPResponse:
        """
        Posts the current clients server count to a service.

        Parameters
        -----------
        service: Optional[:class:`str`]
            The service to post to. Can be `None` to post to all services or `custom` to use the custom post method.
        """
        servers = await self.server_count()
        users = await self.user_count()
        connections = await self.voice_connections()
        return await self.manual_post(servers, service, users, connections)
    
    async def manual_post(
        self, server_count, service = None,
        user_count = None, voice_connections = None
    ) -> HTTPResponse:
        """
        Manually posts a server count to a service.

        Parameters
        -----------
        server_count: :class:`int`
            The server count to post to the service.
        service: Optional[:class:`str`]
            The service to post to. Can be `None` to post to all services or `custom` to use the custom post method.
        user_count: Optional[:class:`int`]
            The user count to post to the service.
        voice_connections: Optional[:class:`int`]
            The voice connection count to post to the service.
        """
        if service == 'custom' and hasattr(self, 'on_custom_post'):
            return await self.on_custom_post(
                self, server_count = server_count,
                user_count = user_count,
                voice_connections = voice_connections
            )
        if len(self.api_keys) == 0:
            raise APIKeyException('No API Keys available')
        if not service or len(service) == 0:
            responses = {}
            keys = list(self.api_keys.keys())
            if hasattr(self, 'on_custom_post'):
                keys.append('custom')
            for key in keys:
                responses.append(await self.manual_post(
                    server_count = server_count,
                    service = key, user_count = user_count,
                    voice_connections = voice_connections
                ))
            return responses
        _service = Service.get(service)
        key = self.get_key(service)
        if not key or len(key) == 0:
            raise APIKeyException(f'Service {service} has no API key')
        try:
            response = await _service._post(
                self.http, self.client_id, key, server_count, user_count,
                voice_connections, self.shard_id, self.shard_count
            )
            log.debug('Posted to %s: %s', response.raw.url, response.body)
            self.dispatch('post', response)
            return response
        except Exception as error:
            log.debug(
                'Posted to %s failed (%s): %s', error.response.raw.url,
                error.status, error.body
            )
            self.dispatch('post_fail', error)
            raise error

class ClientPoster(Poster):
    """
    A class that posts certain client values to listing sites.

    Parameters
    -----------
    client: class
        The client that a supported library uses to manage the Discord application.
    client_library: :class:`str`
        The library that the client is based on.
    loop: Optional[asyncio.AbstractEventLoop]
        The `asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        `asyncio.get_event_loop()`.
    sharding: Optional[:class:`bool`]
        Whether or not to use sharding values.
    shard_count: Optional[:class:`int`]
        The amount of shards the client has.
    shard_id: Optional[:class:`int`]
        The shard ID the poster us posting for.
    proxy: Optional[:class:`str`]
        Proxy URL.
    proxy_auth: Optional[:class:`aiohttp.BasicAut`h]
        An object that represents proxy HTTP Basic Authorization.
    api_keys: Optional[:class:`dict`]
        A dictionary of API keys with the key being service keys and values being tokens.
    """

    def __init__(self, client, client_library, **options):
        filler = ClientFiller.get(client_library, client)
        super().__init__(
            None, filler.server_count, filler.user_count,
            filler.voice_connections, **options
        )
        self.client = client
        self.client_library = client_library
        self.filler = filler

        self._sharding = options.pop('sharding', True)

    def __repr__(self):
        attrs = [
            ('client', self.client),
            ('client_library', self.client_library),
            ('sharding', self._sharding),
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))
    
    @property
    def client_id(self) -> str or None:
        return self.filler.client_id
    
    @property
    def shard_id(self) -> int or None:
        return self._shard_id or self.filler.shard_id if self._sharding else None
    
    @property
    def shard_count(self) -> int or None:
        return self._shard_count or self.filler.shard_count if self._sharding else None
    
    