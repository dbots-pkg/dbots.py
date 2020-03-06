try:
    import discord
except ModuleNotFoundError:
    print('Discord.py is not installed!')
    quit()
import dbots

# Go to https://requestbin.net and replace the path with the given URL
class TestService(dbots.Service):
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
            path = 'http://requestbin.net/r/XXXXXX',
            query = { 'id': bot_id },
            headers = { 'Authorization': token },
            json = payload
        )

dbots.Service.SERVICE_KEYMAP['test'] = TestService

client = discord.Client()
poster = dbots.ClientPoster(client, 'discord.py', api_keys = {
    'test': 'token'
})

@poster.event
async def on_post(response):
    print('Post:', response)

@poster.event
async def on_post_fail(error):
    print('Post Fail:', error)

@poster.event
async def on_auto_post(response):
    print('Auto-Post:', response)

@poster.event
async def on_auto_post_fail(error):
    print('Auto-Post Fail:', error)

@client.event
async def on_ready():
    print('Logged on as', client.user)
    await poster.post()
    poster.start_loop(10)

@client.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == client.user:
        return

    if message.content.startswith('e> '):
        code = message.content[3:]
        output = ''
        try:
            output = str(eval(code))
        except Exception as e:
            output = str(e)
        await message.channel.send(f'```py\n{output}\n```')

    if message.content.startswith('p>'):
        await poster.post()

client.run('XXX')