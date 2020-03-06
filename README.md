<div align="center">
  <p>
    <img src="static/logo.png" alt="dbots logo" width="200" align="left" />
  </p>
  <h1>dbots<i>.py</i></h1>
  <p>A poster for Discord bot lists</p>
  <p>
    <a href="https://www.pypi.org/package/dbots"><img src="https://img.shields.io/pypi/v/dbots?style=for-the-badge" alt="PyPi version" /></a>
    <a href="https://www.pypi.org/package/dbots"><img src="https://img.shields.io/pypi/dm/dbots?style=for-the-badge" alt="PyPi downloads" /></a>
    <a href="https://libraries.io/pypi/dbots"><img src="https://img.shields.io/librariesio/release/pypi/dbots?style=for-the-badge" alt="Dependencies" /></a>
  </p>
</div>

# Table of Contents
- [About](#about)
- [Installing](#installing)
- [Examples](#examples)
  - [Example with client](#example-with-client)
  - [Example without client](#example-without-client)
- [Services](#services)
  - [Supported Services](#supported-services)
  - [Adding Custom Services](#adding-custom-services)
  - [Adding a custom post function](#adding-a-custom-post-function)
- [Other Links](#other-links)

## About
`dbots` helps [Discord](https://discordapp.com) bot developers group all your statistic posting needs into one poster, complete with seperate posting, and a loop to post to all services every `n` seconds.

## Installing
**Python 3.6 or higher is required!**
You can install dbots by running this command:
```sh
# Linux/macOS
python3 -m pip install -U dbots

# Windows
py -3 -m pip install -U dbots
```

## Examples

See other examples [here](/examples).

### Example with client
Currently, only `discord.py` is supported as a usable client. (You can use any derivative of `discord.py` as long as it does not interfere with important properties used by `dbots`.)
```py
import discord
import dbots

client = discord.Client()
poster = dbots.ClientPoster(client, 'discord.py', api_keys = {
    'top.gg': '…',
    'discord.bots.gg': '…'
})

@client.event
async def on_ready():
    print('Logged on as', client.user)
    await poster.post()
    # This posts to all lists every 30 minutes
    # You can stop the loop with `poster.kill_loop()`
    poster.start_loop()

@poster.event
async def on_auto_post(response):
    print('Auto-Post:', response)

"""
You can also define the event you want to get by adding an argument to the decorator.

@poster.event('post')
async def some_function(response):
    print(response)
"""
```

### Example without client
```py
import dbots

client_id = '1234567890'
def server_count():
  return 100
def user_count():
  return 100
def voice_connections():
  return 0

# `server_count`, `user_count`, and `voice_connections` can either be regular functions or coroutines
poster = dbots.Poster(client_id, server_count, user_count, voice_connections, api_keys = {
    'top.gg': '…',
    'discord.bots.gg': '…'
})
```

## Services

### Supported Services
 - [top.gg (formerly discordbots.org)](https://top.gg)
 - [discord.bots.gg](https://discord.bots.gg)
 - *More services will be supported in a future release...*

## #Adding Custom Services
You can add custom services by extending from the base service class (`dbots.Service`) and overriding the `_post` method.  
Make sure to add the custom service class to the service keymap. (`dbots.Service.SERVICE_KEYMAP`) An example of adding a custom service can be shown [here](/examples/costom_service.py).

### Adding a custom post function
You can add a custom post event by defining `on_custom_post` in the initialization of a Poster.  
This function can be used when executing `poster.post('custom')` and when all services are being posted to. 
An example of adding a custom post function can be shown [here](/examples/costom_post.py).

## Contribution
Any contribution may be useful for the package! Make sure when making issues or PRs that the issue has not been addressed yet in a past issue/PR.

## Other Links
- [PyPi](https://www.pypi.org/package/dbots)
- [Libraries.io](https://libraries.io/pypi/dbots)
- Documentation (work in progress)