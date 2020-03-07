from .http import HTTPClient
from .errors import EndpointRequiresToken, ServiceException
from urllib.parse import urlencode as _encode_query

class Service:
    """Represents any postable service."""

    BASE_URL = None

    def __init__(self, token = None, **options):
        self.token = token
        proxy = options.pop('proxy', None)
        proxy_auth = options.pop('proxy_auth', None)
        self.http = HTTPClient(base_url = self.BASE_URL, proxy = proxy, proxy_auth = proxy_auth)

    @staticmethod
    def get(key):
        service = Service.SERVICE_KEYMAP.get(key)
        if not service:
            raise ServiceException("Invalid service")
        return service

    @property
    def has_token(self) -> bool:
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

class BotListSpace(Service):
    """
    Represents the botlist.space's service.
    
    .. seealso::
        `Service's API Documentation <https://docs.botlist.space/>`_
            API Documentation for botlist.space
    """

    BASE_URL = 'https://api.botlist.space/v1'

    @staticmethod
    def _post(
        http_client, bot_id, token,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count = None,
        shard_id = None
    ):
        return http_client.request(
            method = 'POST',
            path = f'{BotListSpace.BASE_URL}/bots/{bot_id}',
            headers = { 'Authorization': token, 'Content-Type': 'application/json' },
            json = { 'server_count': server_count }
        )

    def get_statistics(self) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = '/statistics'
        )

    def get_bots(self) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = '/bots'
        )

    def get_bot(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}'
        )

    def get_bot_votes(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/upvotes',
            requires_token = True
        )

    def get_bot_uptime(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/uptime'
        )

    def get_user(self, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}'
        )

    def get_user_bots(self, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}/bots'
        )

    def get_widget_url(self, bot_id, style = 1, **query) -> str:
        return f'https://api.botlist.space/widget/{bot_id}/{style}?{_encode_query(query)}'

class BotsForDiscord(Service):
    """
    Represents the Bots For Discord's service.
    
    .. seealso::
        `Service's API Documentation <https://docs.botsfordiscord.com/>`_
            API Documentation for Bots For Discord
    """

    BASE_URL = 'https://botsfordiscord.com/api'

    @staticmethod
    def _post(
        http_client, bot_id, token,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count = None,
        shard_id = None
    ):
        return http_client.request(
            method = 'POST',
            path = f'{BotsForDiscord.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def get_bot(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}'
        )

    def get_bot_votes(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}/votes',
            requires_token = True
        )

    def get_user(self, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/user/{user_id}'
        )

    def get_user_bots(self, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/user/{user_id}/bots'
        )

    def get_widget_url(self, bot_id, **query) -> str:
        return f'{BotsForDiscord.BASE_URL}/bot/{bot_id}/widget?{_encode_query(query)}'

class DiscordBotsGG(Service):
    """
    Represents the discord.bots.gg service.
    
    .. seealso::
        `Service's API Documentation <https://discord.bots.gg/docs>`_
            API Documentation for discord.bots.gg
    """

    BASE_URL = 'https://discord.bots.gg/api/v1'

    @staticmethod
    def _post(
        http_client, bot_id, token,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count = None,
        shard_id = None
    ):
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
        return self._request(
            method = 'GET',
            path = '/bots',
            query = query,
            requires_token = True
        )

    def get_bot(self, bot_id, **query) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}',
            query = query,
            requires_token = True
        )

class TopGG(Service):
    """
    Represents the top.gg service.
    
    .. seealso::
        `Service's API Documentation <https://top.gg/api/docs>`_
            API Documentation for top.gg
    """

    BASE_URL = 'https://top.gg/api/'

    @staticmethod
    def _post(
        http_client, bot_id, token,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count = None,
        shard_id = None
    ):
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
        return self._request(
            method = 'GET',
            path = '/bots',
            query = query,
            requires_token = True
        )

    def get_bot(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}',
            requires_token = True
        )

    def get_bot_votes(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/votes',
            requires_token = True
        )

    def check_vote(self, bot_id, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/check',
            query = { 'userId': user_id },
            requires_token = True
        )

    def get_bot_stats(self, bot_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/stats',
            requires_token = True
        )

    def get_user(self, user_id) -> HTTPResponse:
        return self._request(
            method = 'GET',
            path = f'/users/{user_id}',
            requires_token = True
        )

    def get_widget_url(self, bot_id, small_widget = None, **query) -> str:
        subpath = '' if not small_widget else f'/{small_widget}'
        return f'{TopGG.BASE_URL}/widget/{subpath}{bot_id}.svg?{_encode_query(query)}'

Service.SERVICE_KEYMAP = {
    'botlistspace': BotListSpace,
    'botlist.space': BotListSpace,
    'bls': BotListSpace,

    'botsfordiscord': BotsForDiscord,
    'botsfordiscord.com': BotsForDiscord,
    'bfd': BotsForDiscord,

    'discordbotsgg': DiscordBotsGG,
    'discord.bots.gg': DiscordBotsGG,
    'dbotsgg': DiscordBotsGG,
    'dbgg': DiscordBotsGG,

    'topgg': TopGG,
    'top.gg': TopGG,
    'top': TopGG,
    'tgg': TopGG,
    'discordbotsorg': TopGG,
    'discordbots.org': TopGG,
    'dbotsorg': TopGG,
    'dborg': TopGG
}