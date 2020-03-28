from .http import HTTPClient, HTTPResponse
from .errors import EndpointRequiresToken, ServiceException
from urllib.parse import urlencode as _encode_query

class Service:
    """
    Represents any postable service.

    Parameters
    -----------
    token: Optional[:class:`str`]
        The token that the class will use to authorize requests.
    proxy: Optional[:class:`str`]
        Proxy URL.
    proxy_auth: Optional[:class:`aiohttp.BasicAuth`]
        An object that represents proxy HTTP Basic Authorization.

    Attributes
    -----------
    BASE_URL: Optional[:class:`str`]
        The base URL that the service uses for API requests.
    token: :class:`str`
        The token that will be used for the service.
    http: :class:`HTTPClient`
        The HTTP client the service is using.
    """

    BASE_URL = None

    def __init__(self, token = None, **options):
        self.token = token
        proxy = options.pop('proxy', None)
        proxy_auth = options.pop('proxy_auth', None)
        self.http = HTTPClient(base_url = self.BASE_URL, proxy = proxy, proxy_auth = proxy_auth)

    @staticmethod
    def _post():
        """
        Posts statistics to this service.

        Parameters
        -----------
        http_client: :class:`HTTPClient`
            The HTTP client to use when making the request.
        bot_id: :class:`str`
            The client ID that the request will post for.
        token: :class:`str`
            The authorization token for the request.
        http_client: :class:`HTTPClient`
            The HTTP client to use when making the request.
        server_count: int
            The amount of servers that the client is in.
        user_count: Optional[:class:`int`]
            The amount of users that the client cached.
        voice_connections: Optional[:class:`int`]
            The amount of voice connections the client has.
        shard_count: Optional[:class:`int`]
            The shard count the request is posting for.
        shard_id: Optional[:class:`int`]
            The shard ID the request is posting for.
        """
        raise ServiceException('Can\'t post to base service')
        

    @staticmethod
    def get(key: str):
        """
        Gets a service from a key.

        Parameters
        -----------
        key: :class:`str`
            The name of the service to get.
        """
        for service in Service.SERVICES:
            if key.lower() in service.aliases():
                return service
        raise ServiceException('Invalid service')

    @property
    def has_token(self) -> bool:
        """Whether or not the service class has a token."""
        return bool(self.token)

    def _request(self, **options):
        if options.pop('requires_token', False) and not self.token:
            raise EndpointRequiresToken()
        return self.http.request(**options)

    def __repr__(self):
        attrs = [
            ('base_url', self.__class__.BASE_URL),
            ('has_token', self.has_token)
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))

###############################

class Arcane(Service):
    """
    Represents the Arcane Bot Center service.
    
    .. seealso::
        - `Arcane Bot Center Website <https://arcane-center.xyz/>`_
        - `Arcane Bot Center API Documentation <https://arcane-center.xyz/documentation>`_
    """

    BASE_URL = 'https://arcane-center.xyz/api'

    @staticmethod
    def aliases() -> list:
        return [
            'arcanebotcenter', 'arcanecenter', 'arcane-botcenter.xyz', 'arcanebotcenter.xyz',
            'arcane-center.xyz', 'arcanecenter.xyz', 'arcane', 'abc'
        ]

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0,
        shard_count: int = None, shard_id: int = None
    ) -> HTTPResponse:
        payload = {
            'server_count': server_count,
            'member_count': user_count,
        }
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method = 'POST',
            path = f'{Arcane.BASE_URL}/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = payload
        )

class BotListSpace(Service):
    """
    Represents the botlist.space service.
    
    .. seealso::
        - `botlist.space Website <https://botlist.space/>`_
        - `botlist.space API Documentation <https://docs.botlist.space/>`_
    """

    BASE_URL = 'https://api.botlist.space/v1'

    @staticmethod
    def aliases() -> list:
        return ['botlistspace', 'botlist.space', 'bls']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{BotListSpace.BASE_URL}/bots/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def get_statistics(self) -> HTTPResponse:
        """|httpres|\n\n Gets the statistics of this service."""
        return self._request(
            method = 'GET',
            path = '/statistics'
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n\n Gets a list of bots on this service."""
        return self._request(
            method = 'GET',
            path = '/bots'
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}'
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/upvotes',
            requires_token = True
        )

    def get_bot_uptime(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the uptime of a bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/uptime'
        )

    def get_user(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}'
        )

    def get_user_bots(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user's bots listed for this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}/bots'
        )

    def get_widget_url(self, bot_id: str, style = 1, **query) -> str:
        """
        Gets the widget URL for this bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        style: Optional[:class:`int`]
            The style of the widget.
        **query
            The query string to append to the URL.
        """
        return f'https://api.botlist.space/widget/{bot_id}/{style}?{_encode_query(query)}'

class BotsForDiscord(Service):
    """
    Represents the Bots For Discord service.
    
    .. seealso::
        - `Bots For Discord Website <https://botsfordiscord.com/>`_
        - `Bots For Discord API Documentation <https://docs.botsfordiscord.com/>`_
    """

    BASE_URL = 'https://botsfordiscord.com/api'

    @staticmethod
    def aliases() -> list:
        return ['botsfordiscord', 'botsfordiscord.com', 'bfd']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{BotsForDiscord.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}'
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}/votes',
            requires_token = True
        )

    def get_user(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/user/{user_id}'
        )

    def get_user_bots(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user's bots listed for this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/user/{user_id}/bots'
        )

    def get_widget_url(self, bot_id: str, **query) -> str:
        """
        Gets the widget URL for this bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return f'{BotsForDiscord.BASE_URL}/bot/{bot_id}/widget?{_encode_query(query)}'

class BotsOfDiscord(Service):
    """
    Represents the Bots Of Discord service.
    
    .. seealso::
        - `Bots Of Discord Website <https://b-o-d.cf/>`_
    """

    BASE_URL = 'https://www.b-o-d.cf/api'

    @staticmethod
    def aliases() -> list:
        return ['botsofdiscord', 'b-o-d', 'b-o-d.cf']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'server_count': server_count }
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method = 'POST',
            path = f'{BotsOfDiscord.BASE_URL}/bots/stats',
            headers = { 'Authorization': token },
            json = payload
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's stats on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}/stats'
        )

    def get_bot_votes(self) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted this bot on this service.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/votes',
            requires_token = True
        )

    def get_user(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}'
        )

class DiscordBotsGG(Service):
    """
    Represents the Discord Bots service.
    
    .. seealso::
        - `Discord Bots Website <https://discord.bots.gg/>`_
        - `Discord Bots API Documentation <https://discord.bots.gg/docs>`_
    """

    BASE_URL = 'https://discord.bots.gg/api/v1'

    @staticmethod
    def aliases() -> list:
        return ['discordbotsgg', 'discord.bots.gg', 'botsgg', 'bots.gg', 'dbots']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'guildCount': server_count }
        if shard_id and shard_count:
            payload['shardId'] = shard_id
            payload['shardCount'] = shard_count
        return http_client.request(
            method = 'POST',
            path = f'{DiscordBotsGG.BASE_URL}/bots/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = payload
        )

    def get_bots(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.

        Parameters
        -----------
        **query
            The query string to append to the URL.
        """
        return self._request(
            method = 'GET',
            path = '/bots',
            query = query,
            requires_token = True
        )

    def get_bot(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}',
            query = query,
            requires_token = True
        )

class TopGG(Service):
    """
    Represents the Top.gg service.
    
    .. seealso::
        - `Top.gg Website <https://top.gg/>`_
        - `Top.gg API Documentation <https://top.gg/api/docs>`_
    """

    BASE_URL = 'https://top.gg/api'

    @staticmethod
    def aliases() -> list:
        return ['topgg', 'top.gg', 'top']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'server_count': server_count }
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
            payload['shard_count'] = shard_count
        return http_client.request(
            method = 'POST',
            path = f'{TopGG.BASE_URL}/bots/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = payload
        )

    def get_bots(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.

        Parameters
        -----------
        **query
            The query string to append to the URL.
        """
        return self._request(
            method = 'GET',
            path = '/bots',
            query = query,
            requires_token = True
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}',
            requires_token = True
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/votes',
            requires_token = True
        )

    def user_voted(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/check',
            query = { 'userId': user_id },
            requires_token = True
        )

    def get_bot_stats(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's stats listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/stats',
            requires_token = True
        )

    def get_user(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}',
            requires_token = True
        )

    def get_widget_url(self, bot_id: str, small_widget: str = None, **query) -> str:
        """
        Gets the widget URL for this bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        small_widget: Optional[:class:`str`]
            The sub-path name to turn the widget into a badge. (i.e. owner)
        **query
            The query string to append to the URL.
        """
        subpath = '' if not small_widget else f'/{small_widget}'
        return f'{TopGG.BASE_URL}/widget/{subpath}{bot_id}.svg?{_encode_query(query)}'

Service.SERVICES = [
    Arcane, BotListSpace, BotsForDiscord, DiscordBotsGG, TopGG
]