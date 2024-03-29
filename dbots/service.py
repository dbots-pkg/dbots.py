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

    def __init__(self, token=None, **options):
        self.token = token
        proxy = options.pop('proxy', None)
        proxy_auth = options.pop('proxy_auth', None)
        self.http = HTTPClient(base_url=self.BASE_URL, proxy=proxy, proxy_auth=proxy_auth)

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


class BladeList(Service):
    """
    Represents the BladeList service.

    .. seealso::
        - `BladeList Website <https://bladelist.gg/>`_
        - `BladeList API Documentation <https://docs.bladelist.gg/en/latest/api/index.html>`_
    """

    BASE_URL = 'https://api.bladelist.gg'

    @staticmethod
    def aliases() -> list:
        return ['bladebotlist', 'bladebotlist.xyz', 'bladelist', 'bladelist.gg']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'server_count': server_count}
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method='PUT',
            path=f'{BladeList.BASE_URL}/bots/{bot_id}/',
            headers={'Authorization': token, 'Content-Type': 'application/json'},
            json=payload
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot listed on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )


class Blist(Service):
    """
    Represents the Blist service.

    .. seealso::
        - `Blist Website <https://blist.xyz/>`_
        - `Blist API Documentation <https://blist.xyz/docs/>`_
    """

    BASE_URL = 'https://blist.xyz/api/v2'

    @staticmethod
    def aliases() -> list:
        return ['blist', 'blist.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'server_count': server_count}
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{Blist.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/user/{user_id}'
        )

    def get_user_bots(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user's bots listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/user/{user_id}/bots'
        )

    def get_user_servers(self, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the user's servers listed on this service.

        Parameters
        -----------
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/user/{user_id}/servers'
        )

    def get_server(self, server_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the server listed on this service.

        Parameters
        -----------
        server_id: :class:`str`
            The server's ID.
        """
        return self._request(
            method='GET',
            path=f'/server/{server_id}'
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
            method='GET',
            path=f'/bot/{bot_id}/stats'
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
            method='GET',
            path=f'/bot/{bot_id}/votes',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_reviews(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's reviews on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/{bot_id}/reviews',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_widget_url(self, bot_id: str, widget_type: str = 'normal', **query) -> str:
        """
        Gets the widget URL for this bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        widget_type: Optional[:class:`str`]
            The type of widget to show.
        **query
            The query string to append to the URL.
        """
        query['type'] = widget_type
        return f'{Blist.BASE_URL}/widget/{bot_id}.svg?{_encode_query(query)}'


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
        return ['botsondiscord', 'bots.ondiscord.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{BotsOnDiscord.BASE_URL}/bots/{bot_id}/guilds',
            headers={'Authorization': token},
            json={'guildCount': server_count}
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
            method='GET',
            path=f'/bots/{bot_id}/review',
            headers={'Authorization': self.token},
            query={'owner': user_id},
            requires_token=True
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
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{Carbon.BASE_URL}/data/botdata.php',
            json={
                'key': token,
                'servercount': server_count
            }
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
        return self._request(
            method='GET',
            path='/api/listedbots'
        )


class DBots(Service):
    """
    Represents the DBots service.

    .. seealso::
        - `DBots Website <https://dbots.co/>`_
        - `DBots API Documentation <https://docs.dbots.co/>`_
    """

    BASE_URL = 'https://dbots.co/api/v1'

    @staticmethod
    def aliases() -> list:
        return ['dbots', 'dbots.co']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{DBots.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': token},
            json={'guildCount': server_count}
        )

    def get_audit(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's audit logs.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/log',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def regen_token(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Regenerates the bot API token.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/keys/regen',
            headers={'Authorization': self.token},
            requires_token=True
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
        return ['discordboats', 'discord.boats']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{DiscordBoats.BASE_URL}/bot/{bot_id}',
            headers={'Authorization': token},
            json={'server_count': server_count}
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
            method='GET',
            path=f'/bot/{bot_id}'
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
            method='GET',
            path=f'/user/{user_id}'
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
            method='GET',
            path=f'/bot/{bot_id}/voted',
            query={'id': user_id}
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
    Represents the Discord Bot List service.

    .. seealso::
        - `Discord Bot List Website <https://discordbotlist.com/>`_
        - `Discord Bot List API Documentation <https://discordbotlist.com/api-docs/>`_
    """

    BASE_URL = 'https://discordbotlist.com/api/v1'

    @staticmethod
    def aliases() -> list:
        return ['discordbotlist', 'discordbotlist.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'guilds': server_count}
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
        if user_count:
            payload['users'] = user_count
        if voice_connections:
            payload['voice_connections'] = voice_connections
        return http_client.request(
            method='POST',
            path=f'{DiscordBotList.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': f'Bot {token}'},
            json=payload
        )


class DiscordBotlistEU(Service):
    """
    Represents the DiscordBotlistEU service.

    .. seealso::
        - `DiscordBotlistEU Website <https://discord-botlist.eu/>`_
        - `DiscordBotlistEU API Documentation <https://docs.discord-botlist.eu/>`_
    """

    BASE_URL = 'https://api.discord-botlist.eu/v1'

    @staticmethod
    def aliases() -> list:
        return ['dbleu', 'discordbotlisteu']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{DiscordBotlistEU.BASE_URL}/update',
            headers={'Authorization': f'Bearer {token}'},
            json={'serverCount': server_count}
        )

    def get_bot(self) -> HTTPResponse:
        """|httpres|\n\nGets this bot's data."""
        return self._request(
            method='GET',
            path='/ping',
            headers={'Authorization': f'Bearer {self.token}'},
            requires_token=True
        )

    def get_analytics(self) -> HTTPResponse:
        """|httpres|\n\nGets this bot's analytics."""
        return self._request(
            method='GET',
            path='/analytics',
            headers={'Authorization': f'Bearer {self.token}'},
            requires_token=True
        )

    def get_votes(self) -> HTTPResponse:
        """|httpres|\n\nGets this bot's votes."""
        return self._request(
            method='GET',
            path='/votes',
            headers={'Authorization': f'Bearer {self.token}'},
            requires_token=True
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
        return ['discordbotsgg', 'discord.bots.gg']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'guildCount': server_count}
        if shard_id and shard_count:
            payload['shardId'] = shard_id
            payload['shardCount'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{DiscordBotsGG.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path='/bots',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
        )


class DiscordExtremeList(Service):
    """
    Represents the Discord Extreme List service.

    .. seealso::
        - `Discord Extreme List Website <https://discordextremelist.xyz/>`_
        - `Discord Extreme List API Documentation <https://discordextremelist.xyz/docs>`_
    """

    BASE_URL = 'https://api.discordextremelist.xyz/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordextremelist', 'discordextremelist.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'guildCount': server_count}
        if shard_id and shard_count:
            payload['shardCount'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{DiscordExtremeList.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
        )

    def get_statistics(self) -> HTTPResponse:
        """|httpres|\n
        Gets the statistics of this service.
        """
        return self._request(
            method='GET',
            path='/stats'
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
            method='GET',
            path=f'/bot/{bot_id}'
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
            method='GET',
            path=f'/user/{user_id}'
        )


class DiscordLabs(Service):
    """
    Represents the Discord Labs service.

    .. seealso::
        - `Discord Labs Website <https://bots.discordlabs.org/>`_
        - `Discord Labs API Documentation <https://docs.discordlabs.org/#/api>`_
    """

    BASE_URL = 'https://bots.discordlabs.org/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordlabs', 'discordlabs.org']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'server_count': server_count, 'token': token}
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{DiscordLabs.BASE_URL}/bot/{bot_id}/stats',
            json=payload
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
            method='GET',
            path=f'/bot/{bot_id}',
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the votes for this bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/{bot_id}/votes',
        )


class DiscordListSpace(Service):
    """
    Represents the discordlist.space service.

    .. seealso::
        - `discordlist.space Website <https://discordlist.space/>`_
        - `discordlist.space API Documentation <https://docs.discordlist.space/>`_
    """

    BASE_URL = 'https://api.discordlist.space/v2'

    @staticmethod
    def aliases() -> list:
        return ['discordlistspace', 'discordlist.space', 'botlistspace', 'botlist.space']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{DiscordListSpace.BASE_URL}/bots/{bot_id}',
            headers={'Authorization': token, 'Content-Type': 'application/json'},
            json={'server_count': server_count}
        )

    def get_statistics(self) -> HTTPResponse:
        """|httpres|\n\n Gets the statistics of this service."""
        return self._request(
            method='GET',
            path='/statistics'
        )

    def get_languages(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets all the available languages that bots or servers can set as their language.

        Parameters
        -----------
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path='/statistics',
            query=query
        )

    def get_tags(self, **query) -> HTTPResponse:
        """|httpres|\n
        Gets all available tags for use on bots or servers.

        Parameters
        -----------
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path='/tags',
            query=query
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
            method='GET',
            path='/bots',
            query=query
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
            method='GET',
            path=f'/bots/{bot_id}'
        )

    def get_bot_reviews(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the reviews of a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/reviews',
            query=query
        )

    def get_bot_analytics(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the analytics on a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/analytics',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}/upvotes',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_user_upvote(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks if a specific user has upvoted the bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/upvotes/status/{user_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_upvote_leaderboard(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the top upvoters of this month.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/upvotes/leaderboard',
            query=query
        )

    def get_audit_log(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the bot listing audit log.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/audit',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_owners(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets the owners of the bot listing.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/owners',
            query=query
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
            method='GET',
            path=f'/users/{user_id}'
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
            method='GET',
            path=f'/users/{user_id}/bots',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_widget_url(self, bot_id: str, style: int = 1, **query) -> str:
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
        return f'https://api.discordlist.space/widget/{bot_id}/{style}?{_encode_query(query)}'


class DiscordListology(Service):
    """
    Represents the DiscordListology service.

    .. seealso::
        - `DiscordListology Website <https://discordlistology.com/>`_
        - `DiscordListology API Documentation <https://discordlistology.com/developer/documentation/>`_
    """

    BASE_URL = 'https://discordlistology.com/api/v1'

    @staticmethod
    def aliases() -> list:
        return ['discordlistology', 'discordlistology.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'servers': server_count}
        if shard_id and shard_count:
            payload['shards'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{DiscordListology.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/bots/{bot_id}/stats',
        )

    def user_voted_bot(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has voted for a bot on this service.
        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/hasvoted/{user_id}'
        )

    def get_guild_stats(self, guild_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the guild's stats listed on this service.
        Parameters
        -----------
        guild_id: :class:`str`
            The guild's ID.
        """
        return self._request(
            method='GET',
            path=f'/guilds/{guild_id}/stats',
        )

    def user_voted_guild(self, guild_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has voted for a guild on this service.
        Parameters
        -----------
        guild_id: :class:`str`
            The guild's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/guilds/{guild_id}/hasvoted/{user_id}'
        )


class DiscordServices(Service):
    """
    Represents the DiscordServices service.

    .. seealso::
        - `DiscordServices Website <https://discordservices.net/>`_
        - `DiscordServices API Documentation <https://discordservices.net/docs/api/>`_
    """

    BASE_URL = 'https://api.discordservices.net'

    @staticmethod
    def aliases() -> list:
        return ['discordservices', 'discordservices.net']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'servers': server_count}
        if shard_id and shard_count:
            payload['shards'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{DiscordServices.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
        )

    def post_news(self, bot_id: str, title: str, content: str) -> HTTPResponse:
        """|httpres|\n
        Posts news to your bot page.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        title: :class:`str`
            The title of the post.
        content: :class:`str`
            The content of the post.
        """
        return self._request(
            method='POST',
            path=f'/bot/{bot_id}/news',
            json={
                'title': title,
                'content': content,
                'error': False
            },
            headers={'Authorization': self.token},
            requires_token=True
        )

    def post_commands(self, bot_id: str, commands: list) -> HTTPResponse:
        """|httpres|\n
        Posts commands info to your bot page.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        commands: :class:`list`
            The command info to post.
        """
        return self._request(
            method='POST',
            path=f'/bot/{bot_id}/commands',
            json=commands,
            headers={'Authorization': self.token},
            requires_token=True
        )


class DiscordsCom(Service):
    """
    Represents the Discords.com service (formerly Bots For Discord).

    .. seealso::
        - `Discords.com Website <https://discords.com/bots>`_
        - `Discords.com API Documentation <https://docs.botsfordiscord.com/>`_
    """

    BASE_URL = 'https://discords.com/bots/api'

    @staticmethod
    def aliases() -> list:
        return ['botsfordiscord', 'botsfordiscord.com', 'discords', 'discords.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{DiscordsCom.BASE_URL}/bot/{bot_id}',
            headers={'Authorization': token, 'Content-Type': 'application/json'},
            json={'server_count': server_count}
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
            method='GET',
            path=f'/bot/{bot_id}'
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/{bot_id}/votes',
            headers={'Authorization': self.token, 'Content-Type': 'application/json'},
            requires_token=True
        )

    def get_bot_votes_12h(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the list of people who voted a bot in the last 12 hours.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/{bot_id}/votes12h',
            headers={'Authorization': self.token, 'Content-Type': 'application/json'},
            requires_token=True
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
            method='GET',
            path=f'/user/{user_id}'
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
            method='GET',
            path=f'/user/{user_id}/bots'
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
        return f'{DiscordsCom.BASE_URL}/bot/{bot_id}/widget?{_encode_query(query)}'


class Disforge(Service):
    """
    Represents the Disforge service.

    .. seealso::
        - `Disforge Website <https://disforge.com/bots/>`_
        - `Disforge API Documentation <https://disforge.com/developer/>`_
    """

    BASE_URL = 'https://disforge.com/api'

    @staticmethod
    def aliases() -> list:
        return ['disforge', 'disforge.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{Disforge.BASE_URL}/botstats/{bot_id}',
            headers={'Authorization': token},
            json={'servers': server_count}
        )

    def get_homepage(self) -> HTTPResponse:
        """|httpres|\n\nRetreives the data shown on the homepage."""
        return self._request(
            method='GET',
            path='/home'
        )

    def get_stats(self) -> HTTPResponse:
        """|httpres|\n\nRetreives statistics about Disforge."""
        return self._request(
            method='GET',
            path='/stats'
        )


class FatesList(Service):
    """
    Represents the FatesList service.

    .. seealso::
        - `FatesList Website <https://fateslist.xyz/>`_
        - `FatesList API Documentation <https://apidocs.fateslist.xyz/>`_
    """

    BASE_URL = 'https://fateslist.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['fateslist', 'fateslist.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{FatesList.BASE_URL}/botstats/{bot_id}',
            headers={'Authorization': token},
            json={'servers': server_count}
        )

    def get_bot_promotion(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot promotion.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/promotions'
        )

    def add_promotion(self, bot_id: str, promotion: dict) -> HTTPResponse:
        """|httpres|\n
        Adds a bot promotion.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        promotion: :class:`dict`
            The promotion payload.
        """
        return self._request(
            method='POST',
            path=f'/bots/{bot_id}/promotions',
            headers={'Authorization': self.token},
            json=promotion,
            requires_token=True
        )

    def delete_promotion(self, bot_id: str, promotion_id: str) -> HTTPResponse:
        """|httpres|\n
        Deletes a bot promotion.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        promotion_id: :class:`str`
            The promotion ID.
        """
        return self._request(
            method='DELETE',
            path=f'/bots/{bot_id}/promotions',
            json={'promo_id', promotion_id},
            headers={'Authorization': self.token},
            requires_token=True
        )

    def edit_promotion(self, bot_id: str, promotion: dict) -> HTTPResponse:
        """|httpres|\n
        Edits a bot promotion.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        promotion: :class:`dict`
            The promotion payload.
        """
        return self._request(
            method='PATCH',
            path=f'/bots/{bot_id}/promotions',
            headers={'Authorization': self.token},
            json=promotion,
            requires_token=True
        )

    def regenerate_token(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Regenerates the API token.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='PATCH',
            path=f'/bots/{bot_id}/token',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_random_bot(self) -> HTTPResponse:
        """|httpres|\n\nGets a random bot."""
        return self._request(
            method='GET',
            path='/bots/random'
        )

    def get_bot(self, bot_id: str, **query) -> HTTPResponse:
        """|httpres|\n
        Gets a bot from the API.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}',
            query=query,
            headers={'Authorization': self.token}
        )

    def get_bot_commands(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Get a bot's commands.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/commands'
        )

    def add_bot_command(self, bot_id: str, command: dict, **query) -> HTTPResponse:
        """|httpres|\n
        Adds a bot promotion.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        command: :class:`dict`
            The command payload.
        **query
            The query string to append to the URL.
        """
        return self._request(
            method='POST',
            path=f'/bots/{bot_id}/commands',
            headers={'Authorization': self.token},
            query=query,
            json=command,
            requires_token=True
        )

    def delete_bot_command(self, bot_id: str, command_id: str) -> HTTPResponse:
        """|httpres|\n
        Deletes a bot's command.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        command_id: :class:`str`
            The command ID.
        """
        return self._request(
            method='DELETE',
            path=f'/bots/{bot_id}/commands',
            json={'id', command_id},
            headers={'Authorization': self.token},
            requires_token=True
        )

    def edit_bot_command(self, bot_id: str, command: dict) -> HTTPResponse:
        """|httpres|\n
        Edits a bot's command.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        command: :class:`dict`
            The command payload.
        """
        return self._request(
            method='PATCH',
            path=f'/bots/{bot_id}/commands',
            headers={'Authorization': self.token},
            json=command,
            requires_token=True
        )

    def get_votes(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the number of votes a user gave to a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='PATCH',
            path=f'/bots/{bot_id}/votes',
            headers={'Authorization': self.token},
            json={'user_id': user_id},
            requires_token=True
        )

    def get_votes_timestamped(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the number of votes a user gave to a bot with timestamps.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='PATCH',
            path=f'/bots/{bot_id}/votes/timestamped',
            headers={'Authorization': self.token},
            json={'user_id': user_id},
            requires_token=True
        )


class InfinityBotList(Service):
    """
    Represents the Infinity Bot List service.

    .. seealso::
        - `Infinity Bot List Website <https://infinitybotlist.com/>`_
        - `Infinity Bot List API Documentation <https://docs.infinitybotlist.com/>`_
    """

    BASE_URL = 'https://api.infinitybotlist.com'

    @staticmethod
    def aliases() -> list:
        return ['infinitybotlist', 'infinitybotlist.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'botid': bot_id, 'servers': server_count}
        if shard_id and shard_count:
            payload['shards'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{InfinityBotList.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/bot/{bot_id}'
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
            method='GET',
            path=f'/user/{user_id}'
        )


class Listcord(Service):
    """
    Represents the Listcord service.

    .. seealso::
        - `Listcord Website <https://listcord.gg/>`_
        - `Listcord API Documentation <https://listcord.gg/docs/>`_
    """

    BASE_URL = 'https://listcord.gg/api'

    @staticmethod
    def aliases() -> list:
        return ['listcord', 'listcord.gg']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{Listcord.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': token},
            json={'server_count': server_count}
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
            method='GET',
            path=f'/bots/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_reviews(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot's reviews.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/reviews',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def user_voted(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets whether a user has voted for a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/voted',
            query={'user_id': user_id},
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_pack(self, pack_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot pack.

        Parameters
        -----------
        pack_id: :class:`str`
            The pack's ID.
        """
        return self._request(
            method='GET',
            path=f'/pack/{pack_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_packs(self) -> HTTPResponse:
        """|httpres|\n\nGets all botpacks."""
        return self._request(
            method='GET',
            path='/packs',
            headers={'Authorization': self.token},
            requires_token=True
        )


class MotionBotlist(Service):
    """
    Represents the MotionBotlist service.

    .. seealso::
        - `MotionBotlist Website <https://www.motiondevelopment.top/bot/>`_
        - `MotionBotlist API Documentation <https://www.motiondevelopment.top/docs/api/intro/>`_
    """

    BASE_URL = 'https://www.motiondevelopment.top/api/v1.2'

    @staticmethod
    def aliases() -> list:
        return ['motion', 'motiondevelopment', 'motionbotlist', 'motiondevelopment.top']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{MotionBotlist.BASE_URL}/bots/{bot_id}/stats',
            headers={'key': token, 'Content-Type': 'application/json'},
            json={'server_count': server_count}
        )

    def get_bot(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}',
            headers={'key': self.token, 'Content-Type': 'application/json'},
            requires_token=True
        )

    def get_bot_votes(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets a bot's reviews.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bots/{bot_id}/votes',
            headers={'key': self.token, 'Content-Type': 'application/json'},
            requires_token=True
        )


class SpaceBotsList(Service):
    """
    Represents the Space Bots List service.

    .. seealso::
        - `Space Bots List Website <https://space-bot-list.xyz/>`_
        - `Space Bots List API Documentation <https://spacebots.gitbook.io/tutorial-en/>`_
    """

    BASE_URL = 'https://space-bot-list.xyz/api'

    @staticmethod
    def aliases() -> list:
        return ['spacebotslist', 'space-bot-list.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{SpaceBotsList.BASE_URL}/bot/{bot_id}',
            headers={'Authorization': token},
            json={
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
            method='GET',
            path=f'/bots/{bot_id}'
        )


class TopCord(Service):
    """
    Represents the TopCord service.

    .. seealso::
        - `TopCord Website <https://topcord.xyz/>`_
        - `TopCord API Documentation <https://docs.topcord.xyz/#/API>`_
    """

    BASE_URL = 'https://api.topcord.xyz'

    @staticmethod
    def aliases() -> list:
        return ['topcord', 'topcord.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'guilds': server_count}
        if shard_id and shard_count:
            payload['shards'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{TopCord.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/bot/{bot_id}',
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n\nLists every bot on this service."""
        return self._request(
            method='GET',
            path='/bots',
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
        return ['topgg', 'top.gg']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'server_count': server_count}
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
            payload['shard_count'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{TopGG.BASE_URL}/bots/{bot_id}/stats',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/users/{user_id}',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path='/bots',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}/stats',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}/votes',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}/check',
            query={'userId': user_id},
            headers={'Authorization': self.token},
            requires_token=True
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


class VoidBots(Service):
    """
    Represents the Void Bots service.

    .. seealso::
        - `Void Bots Website <https://voidbots.net/>`_
        - `Void Bots API Documentation <https://www.motiondevelopment.top/docs/api/intro/>`_
    """

    BASE_URL = 'https://api.voidbots.net'

    @staticmethod
    def aliases() -> list:
        return ['voidbots', 'voidbots.net']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'server_count': server_count}
        if shard_id and shard_count:
            payload['shard_count'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{VoidBots.BASE_URL}/bot/stats/{bot_id}',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/bot/info/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def user_voted(self, bot_id: str, user_id: str) -> HTTPResponse:
        """|httpres|\n
        Checks whether or not a user has voted for a bot on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        user_id: :class:`str`
            The user's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/voted/{bot_id}/{user_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_reviews(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's reviews on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/reviews/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_bot_analytics(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Gets the bot's analytics on this service.

        Parameters
        -----------
        bot_id: :class:`str`
            The bot's ID.
        """
        return self._request(
            method='GET',
            path=f'/bot/analytics/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
        )


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
        return ['wonderbotlist', 'wonderbotlist.com']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        payload = {'serveurs': server_count}
        if shard_id and shard_count:
            payload['shard'] = shard_count
        return http_client.request(
            method='POST',
            path=f'{WonderBotList.BASE_URL}/bot/{bot_id}',
            headers={'Authorization': token},
            json=payload
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
            method='GET',
            path=f'/bots/{bot_id}',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/user/{user_id}',
            headers={'Authorization': self.token},
            requires_token=True
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
        return ['yabl', 'yabl.xyz']

    @staticmethod
    def _post(
        http_client: HTTPClient, bot_id: str, token: str,
        server_count: int = 0, user_count: int = 0,
        voice_connections: int = 0, shard_count: int = None,
        shard_id: int = None
    ) -> HTTPResponse:
        return http_client.request(
            method='POST',
            path=f'{YABL.BASE_URL}/bot/{bot_id}/stats',
            headers={'Authorization': token},
            json={'guildCount': server_count}
        )

    def invalidate(self, bot_id: str) -> HTTPResponse:
        """|httpres|\n
        Invalidates the token being used in the request.
        """
        return self._request(
            method='GET',
            path='/token/invalidate',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path=f'/bots/{bot_id}'
        )

    def get_random_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets 20 random bots from this service.
        """
        return self._request(
            method='GET',
            path='/bots'
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
            method='GET',
            path=f'/bots/user/{user_id}'
        )

    def get_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of bots on this service.
        """
        return self._request(
            method='GET',
            path='/bots/all',
            headers={'Authorization': self.token},
            requires_token=True
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
            method='GET',
            path='/bots/page',
            query=query,
            headers={'Authorization': self.token},
            requires_token=True
        )

    def get_unverified_bots(self) -> HTTPResponse:
        """|httpres|\n
        Gets a list of unverified bots on this service.
        """
        return self._request(
            method='GET',
            path='/bots/unverified',
            headers={'Authorization': self.token},
            requires_token=True
        )


Service.SERVICES = [
    BladeList, Blist, BotsOnDiscord, Carbon, DBots,
    DiscordBoats, DiscordBotList, DiscordBotlistEU, DiscordBotsGG,
    DiscordExtremeList, DiscordLabs, DiscordListSpace, DiscordListology, DiscordServices,
    DiscordsCom, Disforge, FatesList, InfinityBotList, Listcord, MotionBotlist,
    SpaceBotsList, TopCord, TopGG, VoidBots, WonderBotList, YABL
]
