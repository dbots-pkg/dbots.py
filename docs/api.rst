.. currentmodule:: dbots

API Reference
===============

The following section outlines the API of dbots.

Version Related Info
---------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Classes
--------

.. autoclass:: Poster
    :members:

.. autoclass:: Service
    :members:

.. autoclass:: AsyncLoop
    :members:

HTTP Classes
------------

.. autoclass:: HTTPClient
    :members:

.. autoclass:: HTTPResponse
    :members:

Services
--------

.. autoclass:: Arcane
    :members:

.. autoclass:: BotListSpace
    :members:

.. autoclass:: BotsForDiscord
    :members:

.. autoclass:: BotsOfDiscord
    :members:

.. autoclass:: Carbon
    :members:

.. autoclass:: DiscordBotsGG
    :members:

.. autoclass:: TopGG
    :members: