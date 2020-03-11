import atexit
import aiohttp
import json
import logging
import sys
from urllib.parse import urlencode as _encode_query
from .errors import HTTPException, HTTPUnauthorized, HTTPForbidden, HTTPNotFound
from . import __version__

log = logging.getLogger(__name__)

class HTTPClient:
    """Represents an HTTP client that can send requests."""

    def __init__(self, base_url=None, proxy=None, proxy_auth=None):
        self.__session = aiohttp.ClientSession()
        self.base_url = base_url
        self.proxy = proxy
        self.proxy_auth = proxy_auth

        user_agent = 'dbots (https://github.com/dbots-pkg/dbots.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        atexit.register(self.close)

    def __repr__(self):
        attrs = [
            ('base_url', self.base_url)
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))

    def recreate_session(self):
        if self.__session.closed:
            self.__session = aiohttp.ClientSession()

    async def request(self, method, path, **kwargs):
        # Evaluate kwargs

        if not 'headers' in kwargs:
            kwargs['headers'] = {
                'User-Agent': self.user_agent,
            }
        else:
            kwargs['headers']['User-Agent'] = self.user_agent

        if 'json' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = HTTPClient.to_json(kwargs.pop('json'))
        
        if self.proxy is not None:
            kwargs['proxy'] = self.proxy
        if self.proxy_auth is not None:
            kwargs['proxy_auth'] = self.proxy_auth

        url = path
        if self.base_url:
            url = self.base_url + path
        
        if 'query' in kwargs:
            url = url + '?' + _encode_query(kwargs['query'])
            del kwargs['query']

        async with self.__session.request(method, url, **kwargs) as r:
            log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), r.status)

            response = HTTPResponse(r, await r.text(encoding='utf-8'))
            
            if 300 > r.status >= 200:
                log.debug('%s %s has received %s', method, url, response.body)
                return response
            elif r.status == 401:
                raise HTTPUnauthorized(response)
            elif r.status == 403:
                raise HTTPForbidden(response)
            elif r.status == 404:
                raise HTTPNotFound(response)
            else:
                raise HTTPException(response)

    async def close(self):
        if self.__session:
            await self.__session.close()

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


class HTTPResponse:
    """
    A wrapped response from an :class:`HTTPClient`:.

    Attributes
    -----------
    body: :class:`dict` or :class:`str`
        The body of the response. The response is auto-parsed to json if available.
    text: :class:`str`
        The text body of the response.
    raw: :class:`aiohttp.ClientResponse`
        The raw response from ``aiohttp``.
    status: :class:`int`
        The HTTP status code of the response.
    method: :class:`str`
        The method the request used.
    url: :class:`str`
        The URL of the response.
    """

    def __init__(self, response, text):
        try:
            if response.headers['content-type'] == 'application/json':
                text = json.loads(text)
        except KeyError:
            pass
        self.body = text
        self.text = text
        self.raw = response
        self.status = response.status
        self.method = response.method
        self.url = response.url

    def __repr__(self):
        attrs = [
            ('status', self.status),
            ('method', self.method),
            ('url', self.url)
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))