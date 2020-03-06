import dbots

class CustomService(dbots.Service):
    @staticmethod
    def _post(
        http_client, bot_id, token, server_count = 0, user_count = 0,
        voice_connections = 0, shard_count = None, shard_id = None
    ):
        payload = {
            'server_count': server_count,
            'user_count': user_count,
            'voice_connections': voice_connections
        }
        if shard_id and shard_count:
            payload['shard_id'] = shard_id
            payload['shard_count'] = shard_count
        return http_client.request(
            method = 'POST',
            path = 'http://httpbin.org/post',
            query = { 'id': bot_id },
            headers = { 'Authorization': token },
            json = payload
        )

dbots.Service.SERVICE_KEYMAP['customservice'] = TestService

client_id = '1234567890'

def server_count():
  return 100

def user_count():
  return 100

def voice_connections():
  return 0

poster = dbots.Poster(client_id, server_count, user_count, voice_connections, api_keys = {
    'customservice': '…'
})
