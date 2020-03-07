dbots.py
========
A poster/wrapper for Discord bot lists

.. image:: https://img.shields.io/pypi/v/dbots?style=for-the-badge
   :target: https://www.pypi.org/project/dbots
   :alt: PyPi version
.. image:: https://img.shields.io/pypi/dm/dbots?style=for-the-badge
   :target: https://www.pypi.org/project/dbots
   :alt: PyPI downloads
.. image:: https://img.shields.io/librariesio/release/pypi/dbots?style=for-the-badge
   :target: https://libraries.io/pypi/dbots
   :alt: Dependencies

Table Of Contents
=================

- `About`_
- `Installing`_
- `Examples`_
  - `Example with client`_
  - `Example without client`_
- `Services`_
  - `Supported Services`_
  - `Adding Custom Services`_
  - `Adding a custom post function`_
- `Other Links`_

About
-----
``dbots`` helps `Discord <https://discordapp.com>`_ bot developers group all your statistic posting needs into one poster, complete with seperate posting, and a loop to post to all services every ``n`` seconds.

Installing
----------

**Python 3.6 or higher is required**

You can install dbots by running this command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U dbots

    # Windows
    py -3 -m pip install -U dbots

To install package from the master branch, do the following:

.. code:: sh

    git clone https://github.com/dbots-pkg/dbots.py
    cd dbots.py
    python3 -m pip install -U

Examples
--------

Example with client
~~~~~~~~~~~~~~~~~~~

.. code:: py

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

Example without client
~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

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
  
See more examples `here <https://github.com/dbots-pkg/dbots.py/tree/master/examples>`_.


Services
--------

Supported Services
~~~~~~~~~~~~~~~~~~
 - `top.gg <https://top.gg>`_
 - `discord.bots.gg <https://discord.bots.gg>`_
 - *More services will be supported in a future release...*

Adding Custom Services
~~~~~~~~~~~~~~~~~~~~~~
You can add custom services by extending from the base service class (``dbots.Service``) and overriding the ``_post`` method.  
Make sure to add the custom service class to the service keymap. (``dbots.Service.SERVICE_KEYMAP``) An example of adding a custom service can be shown `here <https://github.com/dbots-pkg/dbots.py/blob/master/examples/custom_service.py>`_.

Adding a custom post function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can add a custom post event by defining ``on_custom_post`` in the initialization of a Poster.  
This function can be used when executing ``poster.post('custom')`` and when all services are being posted to. 
An example of adding a custom post function can be shown `here <https://github.com/dbots-pkg/dbots.py/blob/master/examples/custom_post.py>`_.

Contribution
------------
Any contribution may be useful for the package! Make sure when making issues or PRs that the issue has not been addressed yet in a past issue/PR.

Other Links
-----------

- `PyPi <https://www.pypi.org/project/dbots>`_
- `Libraries.io <https://libraries.io/pypi/dbots>`_
- `Documentation <https://dbots.readthedocs.io/en/latest/index.html>`_
