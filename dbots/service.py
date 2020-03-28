from .http import HTTPClient, HTTPResponse
from .errors import EndpointRequiresToken, ServiceException, PostingUnsupported
from urllib.parse import urlencode as _encode_query
from urllib.parse import quote as _encode_uri

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

    def get_bot_stats(self, bot_id: str) -> HTTPResponse:
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

class BotsOnDiscord(Service):
    """
    Represents the Bots On Discord service.
    
    .. seealso::
        - `Bots On Discord Website <https://bots.ondiscord.xyz/>`_
        - `Bots On Discord API Documentation <https://bots.ondiscord.xyz/info/api/>`_
    """

    BASE_URL = 'https://bots.ondiscord.xyz/bot-api'

    @staticmethod
    def aliases() -> list:
        return ['botsondiscord', 'bots.ondiscord.xyz', 'bod']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{BotsOnDiscord.BASE_URL}/bots/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def check_review(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has reviewed a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/review',
            headers = { 'Authorization': self.token },
            query = { 'owner': user_id },
            requires_token = True
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
        return f'https://bots.ondiscord.xyz/bots/{bot_id}/embed?{_encode_query(query)}'

class Carbon(Service):
    """
    Represents the Carbonitex service.
    
    .. seealso::
        - `Carbonitex Website <https://www.carbonitex.net/Discord/bots/>`_
    """

    BASE_URL = 'https://www.carbonitex.net/discord'

    @staticmethod
    def aliases() -> list:
        return ['carbonitex', 'carbonitex.net', 'carbon']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{Carbon.BASE_URL}/data/botdata.php',
            json = {
                'key': token,
                'servercount': server_count
            }
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/api/listedbots'
        )

class CloudBotList(Service):
    """
    Represents the Cloud Botlist service.
    
    .. seealso::
        - `Cloud Botlist Website <https://cloud-botlist.xyz/>`_
        - `Cloud Botlist API Documentation <https://apollos.gitbook.io/cloud-botlist/>`_
    """

    BASE_URL = 'https://cloud-botlist.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['cloudbotList', 'cloud-botlist.xyz', 'cloudbotList.xyz', 'cloudbl', 'cbl']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0,
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{CloudBotList.BASE_URL}/bots/{bot_id}',
            headers = { 'Authorization': token },
            json = {
                'guilds': server_count,
                'users': user_count
            }
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
            path = f'/bots/{bot_id}'
        )

class CloudList(Service):
    """
    Represents the Cloud List service.
    
    .. seealso::
        - `Cloud List Website <https://www.cloudlist.xyz/>`_
        - `Cloud List API Documentation <https://www.cloudlist.xyz/apidocs/>`_
    """

    BASE_URL = 'https://www.cloudlist.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['cloudlist', 'cloudlistxyz', 'cloudlist.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0,
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{CloudList.BASE_URL}/stats/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'count': server_count }
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
            path = f'/bot/{bot_id}',
            headers = { 'Authorization': self.token },
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
            path = f'/bot/vote/{bot_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

class DBLista(Service):
    """
    Represents the DBLista service.
    
    .. seealso::
        - `DBLista Website <https://dblista.pl/>`_
        - `DBLista API Documentation <https://docs.dblista.pl/>`_
    """

    BASE_URL = 'https://www.cloudlist.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['dblistapl', 'dblista.pl', 'dblista']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str
    ) -> HTTPResponse:
        raise PostingUnsupported()

    def add_bot(self, data: dict) -> HTTPResponse:
        """|httpres|\n
        Updates the bot's listing with the data provided.

        Parameters
        -----------
        data: :class:`dict`
            The data being posted. This should include the ID of the bot.
        """
        return self._request(
            method = 'POST',
            path = '/bots',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def update_bot(self, data: dict) -> HTTPResponse:
        """|httpres|\n
        Updates the bot's listing with the data provided.

        Parameters
        -----------
        data: :class:`dict`
            The data being posted. This should include the ID of the bot.
        """
        return self._request(
            method = 'PUT',
            path = '/bots',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
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
            path = f'/bots/{bot_id}'
        )

    def get_bots(self, page: int = 0) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's stats on this service.

        Parameters
        -----------
        page: :class:`int`
            The page you want to get.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/list/{page}'
        )

    def get_unverified_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of unverified bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots/list/unverified'
        )

    def get_rejected_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of rejected bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots/list/rejected'
        )

    def rate_bot(self, bot_id: str, data: dict) -> HTTPResponse:
        """|httpres|\n
        Adds a rating to a bot on the service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        data: :class:`dict`
            The data being posted. This should include the ID of the bot.
        """
        return self._request(
            method = 'POST',
            path = f'/bots/{bot_id}/rate',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def remove_rating(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Removes a rating from a bot on the service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'DELETE',
            path = f'/bots/{bot_id}/rate',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def remove_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Removes a bot from the service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'DELETE',
            path = f'/bots/{bot_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def search(self, query: str) -> HTTPResponse:
        """|httpres|\n
        Searches for bots on the service.

        Parameters
        -----------
        query: :class:`str`
            The query to search for.
        """
        uri = _encode_uri(query, safe='~()*!.\'')
        return self._request(
            method = 'GET',
            path = f'/bots/search/{uri}'
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
        server_count = 0, shard_count: int = None,
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
            requires_token = True
        )

class DiscordAppsDev(Service):
    """
    Represents the Discord Apps service.
    
    .. seealso::
        - `Discord Apps Website <https://discordapps.dev/>`_
        - `Discord Apps API Documentation <https://discordapps.dev/en-GB/posts/docs/api-v2/>`_
    """

    BASE_URL = 'https://api.discordapps.dev/api/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordappsdev', 'discordapps.dev', 'discordapps', 'dapps']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{DiscordAppsDev.BASE_URL}/bots/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'bot': { 'count': server_count } }
        )

    def get_bots(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots',
        )

    def get_apps(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a list of applications on this service.
        """
        return self._request(
            method = 'GET',
            path = '/apps',
        )

    def get_rpc_apps(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a list of RPC applications on this service.
        """
        return self._request(
            method = 'GET',
            path = '/rpc',
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

    def update_bot(self, bot_id: str, data: dict) -> HTTPResponse:
        """|httpres|\n
        Updates the bot with the data provided.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        data: :class:`dict`
            The data being posted.
        """
        return self._request(
            method = 'POST',
            path = f'/bots/{bot_id}',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

class DiscordBoats(Service):
    """
    Represents the Discord Boats service.
    
    .. seealso::
        - `Discord Boats Website <https://discord.boats/>`_
        - `Discord Boats API Documentation <https://discord.boats/api/docs/>`_
    """

    BASE_URL = 'https://discord.boats/api/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordboats', 'discord.boats', 'dboats']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{DiscordBoats.BASE_URL}/bot/{bot_id}',
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

    def user_voted(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has reviewed a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}/voted',
            query = { 'id': user_id },
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
        return f'{DiscordBoats.BASE_URL}/widget/{bot_id}.svg?{_encode_query(query)}'

class DiscordBotList(Service):
    """
    Represents the Discord Boats service.
    
    .. seealso::
        - `Discord Boats Website <https://discord.boats/>`_
        - `Discord Boats API Documentation <https://discord.boats/api/docs/>`_
    """

    BASE_URL = 'https://discord.boats/api/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordboats', 'discord.boats', 'dboats']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0,
        voice_connections = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'guilds': server_count }
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
        if user_count:
            payload['users'] = user_count
        if voice_connections:
            payload['voice_connections'] = voice_connections
        return http_client.request(
            method = 'POST',
            path = f'{DiscordBotList.BASE_URL}/bots/{bot_id}/stats',
            headers = { 'Authorization': f'Bot {token}' },
            json = payload
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
        return f'https://discordbotlist.com/bots/{bot_id}/widget?{_encode_query(query)}'

class DiscordBotWorld(Service):
    """
    Represents the Discord Bot World service.
    
    .. seealso::
        - `Discord Bot World Website <https://discordbot.world/>`_
        - `Discord Bot World API Documentation <https://discordbot.world/docs/>`_
    """

    BASE_URL = 'https://discordbot.world/api'

    @staticmethod
    def aliases() -> list:
        return ['discordbotworld', 'discordbot.world', 'dbotworld', 'dbw']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{DiscordBotWorld.BASE_URL}/bot/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = { 'guild_count': server_count }
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
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
            path = f'/bots/{bot_id}/info'
        )

    def get_bot_stats(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's stats on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/stats'
        )

    def get_bot_likes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who liked this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/likes',
            headers = { 'Authorization': self.token },
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

class DiscordExtremeList(Service):
    """
    Represents the Discord Extreme List service.
    
    .. seealso::
        - `Discord Extreme List Website <https://discordextremelist.xyz/>`_
        - `Discord Extreme List API Documentation <https://docs.discordextremelist.xyz/>`_
    """

    BASE_URL = 'https://api.discordextremelist.xyz/v1'

    @staticmethod
    def aliases() -> list:
        return ['discordextremelist', 'discordextremelist.xyz', 'discordextremelistxyz', 'del']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{DiscordExtremeList.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'guildCount': server_count }
        )

    def get_statistics(self) -> HTTPResponse:
        """|httpres|\n
        Gets the statistics of this service.
        """
        return self._request(
            method = 'GET',
            path = '/stats',
            headers = { 'Authorization': self.token },
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
            path = f'/bot/{bot_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_bot_stats(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's stats on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/stats'
        )

    def get_bot_likes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who liked this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/likes',
            headers = { 'Authorization': self.token },
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
            path = f'/user/{user_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
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
        return f'{DiscordExtremeList.BASE_URL}/bot/{bot_id}/widget?{_encode_query(query)}'

class DivineDiscordBots(Service):
    """
    Represents the Divine Discord Bots service.
    
    .. seealso::
        - `Divine Discord Bots Website <https://divinediscordbots.com/>`_
        - `Divine Discord Bots API Documentation <https://divinediscordbots.com/api/>`_
    """

    BASE_URL = 'https://divinediscordbots.com'

    @staticmethod
    def aliases() -> list:
        return ['divinediscordbots', 'divinediscordbots.com', 'divinedbots', 'divine', 'ddb']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{DivineDiscordBots.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def get_bot_stats(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the statistics of your bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/{bot_id}/stats'
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
            path = f'/bots/{bot_id}/votes'
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
        return f'{DivineDiscordBots.BASE_URL}/api/widget/{bot_id}.svg?{_encode_query(query)}'

class GlennBotList(Service):
    """
    Represents the Glenn Bot List service.
    
    .. seealso::
        - `Glenn Bot List Website <https://glennbotlist.xyz/>`_
        - `Glenn Bot List API Documentation <https://docs.glennbotlist.xyz/>`_
    """

    BASE_URL = 'https://glennbotlist.xyz/api/v2'

    @staticmethod
    def aliases() -> list:
        return ['glennbotlist', 'glennbotlist.xyz', 'glennbotlist.gg', 'glenn']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{GlennBotList.BASE_URL}/bot/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = { 'serverCount': server_count }
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
            path = f'/bots/{bot_id}/votes',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_profile(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Get a user's profile listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/profile/{user_id}'
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
        return f'https://glennbotlist.xyz/bot/{bot_id}/widget?{_encode_query(query)}'

class LBots(Service):
    """
    Represents the LBots service.
    
    .. seealso::
        - `LBots Website <https://lbots.org/>`_
        - `LBots API Documentation <https://lbots.org/api/docs/>`_
    """

    BASE_URL = 'https://lbots.org/api/v1'

    @staticmethod
    def aliases() -> list:
        return ['lbots', 'lbotsorg', 'lbots.org']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'guild_count': server_count }
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
            payload['shard_count'] = shard_count
        return http_client.request(
            method = 'POST',
            path = f'{LBots.BASE_URL}/bots/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = payload
        )

    def invalidate(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Invalidates the token being used in the request.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/invalidate',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_bot_favorites(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who favorited this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/favorites',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def user_favorited(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has favorited a bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bots/{bot_id}/favorites/user/{user_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def update_panel_guilds(self, bot_id: str, data: dict) -> HTTPResponse:
        """|httpres|\n
        Updates the guilds on the bot's panel.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        data: :class:`dict`
            The data being posted.
        """
        return self._request(
            method = 'POST',
            path = f'/panel/{bot_id}/guilds',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_panel_guild_settings(self, bot_id: str, guild_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who favorited this bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        guild_id: :class:`str`
            The guild's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/panel/{bot_id}/guild/{guild_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def update_panel_guilds(self, bot_id: str, guild_id: str, data: dict) -> HTTPResponse:
        """|httpres|\n
        Gets a guilds settings from the bot's panel.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        guild_id: :class:`str`
            The guild's ID.
        data: :class:`dict`
            The data being posted.
        """
        return self._request(
            method = 'POST',
            path = f'/panel/{bot_id}/guild/{guild_id}/update',
            json = data,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

class ListMyBots(Service):
    """
    Represents the List My Bots service.
    
    .. seealso::
        - `List My Bots Website <https://listmybots.com/>`_
    """

    BASE_URL = 'https://listmybots.com/api/public'

    @staticmethod
    def aliases() -> list:
        return ['listmybots', 'listmybots.com', 'listmybotscom', 'lmb']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{ListMyBots.BASE_URL}/bot/stats',
            headers = { 'Authorization': token },
            json = { 'server_count': server_count }
        )

    def get_statistics(self) -> HTTPResponse:
        """|httpres|\n
        Gets the statistics of this service.
        """
        return self._request(
            method = 'GET',
            path = '/stats',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_current_bot(self) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's info based on the token.
        """
        return self._request(
            method = 'GET',
            path = '/bot/me',
            headers = { 'Authorization': self.token },
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
            path = f'/bot/{bot_id}',
            headers = { 'Authorization': self.token },
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
            path = f'/user/{user_id}',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def user_voted(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has liked the current bot based on your token on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method = 'GET',
            path = f'/bot/me/liked/{user_id}',
            headers = { 'Authorization': self.token },
            query = { 'id': user_id },
            requires_token = True
        )

class MythicalBots(Service):
    """
    Represents the Mythical Bots service.
    
    .. seealso::
        - `Mythical Bots Website <https://mythicalbots.xyz/>`_
        - `Mythical Bots API Documentation <https://docs.mythicalbots.xyz/>`_
    """

    BASE_URL = 'https://mythicalbots.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['mythicalbots', 'mythicalbots.xyz', 'mythicalbotsxyz', 'mythical']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{MythicalBots.BASE_URL}/bot/{bot_id}',
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
            path = f'/bot/{bot_id}/info'
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
        return f'https://mythicalbots.xyz/bot/{bot_id}/embed?{_encode_query(query)}'

class SpaceBotsList(Service):
    """
    Represents the Space Bots List service.
    
    .. seealso::
        - `Space Bots List Website <https://space-bot-list.org/>`_
        - `Space Bots List API Documentation <https://spacebots.gitbook.io/tutorial-en/>`_
    """

    BASE_URL = 'https://space-bot-list.org/api'

    @staticmethod
    def aliases() -> list:
        return ['spacebotslist', 'spacebotlist', 'spacebots', 'space-bot-list.org', 'space', 'sbl']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, user_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{SpaceBotsList.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = {
                'guilds': server_count,
                'users': user_count
            }
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
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
            headers = { 'Authorization': self.token },
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

class WonderBotList(Service):
    """
    Represents the Wonder Bot List service.
    
    .. seealso::
        - `Wonder Bot List Website <https://wonderbotlist.com/>`_
        - `Wonder Bot List API Documentation <https://api.wonderbotlist.com/en/>`_
    """

    BASE_URL = 'https://api.wonderbotlist.com/v1'

    @staticmethod
    def aliases() -> list:
        return ['wonderbotlist', 'wonderbotlist.com', 'wonderbotlistcom', 'wonder', 'wbl']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = { 'serveurs': server_count }
        if shard_id and shard_count:
            payload['shard']: shard_count
        return http_client.request(
            method = 'POST',
            path = f'{WonderBotList.BASE_URL}/bot/{bot_id}',
            headers = { 'Authorization': token },
            json = payload
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

class YABL(Service):
    """
    Represents the YABL service.
    
    .. seealso::
        - `YABL Website <https://yabl.xyz/>`_
        - `YABL API Documentation <https://yabl.xyz/api/>`_
    """

    BASE_URL = 'https://yabl.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['yabl', 'yablxyz', 'yabl.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count = 0
    ) -> HTTPResponse:
        return http_client.request(
            method = 'POST',
            path = f'{YABL.BASE_URL}/bot/{bot_id}/stats',
            headers = { 'Authorization': token },
            json = { 'guildCount': server_count }
        )

    def invalidate(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Invalidates the token being used in the request.
        """
        return self._request(
            method = 'GET',
            path = '/token/invalidate',
            headers = { 'Authorization': self.token },
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
            path = f'/bots/{bot_id}'
        )

    def get_random_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets 20 random bots from this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots'
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
            path = f'/bots/user/{user_id}'
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots/all',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_bots_by_page(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a page of bots on this service.

        Parameters
        -----------
        **query
            The query string to append to the URL.
        """
        return self._request(
            method = 'GET',
            path = '/bots/page',
            query = query,
            headers = { 'Authorization': self.token },
            requires_token = True
        )

    def get_unverified_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of unverified bots on this service.
        """
        return self._request(
            method = 'GET',
            path = '/bots/unverified',
            headers = { 'Authorization': self.token },
            requires_token = True
        )

Service.SERVICES = [
    Arcane, BotListSpace, BotsForDiscord, BotsOfDiscord, BotsOnDiscord, Carbon,
    CloudBotList, CloudList, DBLista, DiscordBotsGG, DiscordAppsDev, DiscordBoats,
    DiscordBotList, DiscordBotWorld, DiscordExtremeList, DivineDiscordBots, GlennBotList,
    LBots, ListMyBots, MythicalBots, SpaceBotsList, TopGG, WonderBotList, YABL
]