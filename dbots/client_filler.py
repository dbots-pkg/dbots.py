from .errors import ClientException

class ClientFiller:
    """A class that gets certain values from a client."""

    def __init__(self, client):
        self.client = client

    @staticmethod
    def get(name, client):
        if not client:
            raise ClientException("No client was given")
        filler = ClientFiller.CLIENT_KEYMAP.get(name)
        if not filler:
            raise ClientException("Invalid client")
        return filler(client)

    def user_count(self) -> int:
        """
        :returns: Returns the number of users the client has.
        """
        return 0

    def server_count(self) -> int:
        """
        :returns: Returns the number of servers the client is in.
        """
        return 0

    def voice_connections(self) -> int:
        """
        :return: Returns the number of voice connections the client has.
        """
        return 0

    @property
    def client_id(self) -> str or None:
        """
        :return: Returns the ID (technically the user ID) of the client.
        """
        return None

    @property
    def shard_id(self) -> int or None:
        """
        :return: Returns the shard ID of the client.
        """
        return None

    @property
    def shard_count(self) -> int or None:
        """
        :return: Returns the amount of shards the client's application has.
        """
        return None

class DiscordPy(ClientFiller):
    """Represents the client filler for discord.py clients."""

    def user_count(self):
        return len(self.client.users)

    def server_count(self):
        return len(self.client.guilds)

    def voice_connections(self):
        return len(self.client.voice_clients)

    @property
    def client_id(self):
        return str(self.client.user.id) if self.client.user else None

    @property
    def shard_id(self):
        if self.client.__class__.__name__ == "AutoShardedClient":
            return None
        elif type(self.client.shard_id) == int:
            return self.client.shard_id
        return None

    @property
    def shard_count(self):
        if self.client.__class__.__name__ == "AutoShardedClient":
            return None
        else:
            return self.client.shard_count

ClientFiller.CLIENT_KEYMAP = {
    'discord.py': DiscordPy,
    'discordpy': DiscordPy,
    'd.py': DiscordPy,
    'dpy': DiscordPy,
}