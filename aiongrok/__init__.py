import json
import logging
import random

import aiohttp

version = '0.0.1'  # type: str

logging.getLogger(__name__).addHandler(logging.NullHandler())


class BaseError(Exception):
    """Common and base exception in hierarchy."""
    pass


class RootError(BaseError):
    """Exception represents root endpoint error."""
    pass


class TunnelError(BaseError):
    """Exception which represents tunnel errors."""
    pass


class Tunnel:
    """Represents single tunnel item."""

    def __init__(self, *, name: str, uri: str, proto: str, public_url: str):
        self.name = name
        self.uri = uri
        self.proto = proto
        self.public_url = public_url

    def __str__(self) -> str:
        return '{}, {}'.format(self.name, self.public_url)


class TunnelsCollection(list):
    """Represents collection of the tunnels."""

    @property
    def any_http_tunnel(self) -> Tunnel:
        """Any random available HTTP tunnel."""
        return self._any_tunnel('http')

    @property
    def any_https_tunnel(self) -> Tunnel:
        """Any random available SSL/TLS tunnel."""
        return self._any_tunnel('https')

    def _any_tunnel(self, proto: str) -> Tunnel:
        random.shuffle(self)
        for tunnel in self:
            if tunnel.proto == proto:
                logging.debug('tunnel with proto {} found'.format(proto))
                return tunnel
        msg = 'any {} tunnel not found'.format(proto)
        logging.warning(msg)
        raise TunnelError(msg)


class Session:
    """Session of the aiongrok."""

    api_url = 'http://127.0.0.1:4040/'
    headers = {'Content-Type': 'application/json'}

    def __init__(self, *, api_url: str = None, headers: dict = None):
        if api_url is not None:
            self.api_url = api_url
        if headers is not None:
            self.headers = headers
        self._session = aiohttp.ClientSession(headers=self.headers)

    def close(self):
        self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._session.close()

    async def get_root(self) -> dict:
        """Gets dict response from GET '/api' endpoint.
        Contains general information.
        """
        async with self._session.get(self._url('api')) as resp:
            data = await resp.json()
            if resp.status != 200:
                msg = 'unable to make root request'
                logging.warning(msg)
                raise RootError(msg)
        logging.debug("got '/api' response:")
        logging.debug(json.dumps(data, indent=4, sort_keys=True))
        return data

    async def get_tunnels(self) -> TunnelsCollection:
        """Gets response from GET '/api/tunnels' endpoint.
        Contains information about all the tunnels.
        """
        async with self._session.get(self._url('api/tunnels')) as resp:
            data = await resp.json()
            if resp.status != 200:
                msg = 'unable to fetch tunnels list'
                logging.warning(msg)
                raise RootError(msg)
        logging.debug("got '/api/tunnels' response:")
        logging.debug(json.dumps(data, indent=4, sort_keys=True))
        tunnels = [self._make_tunnel(item) for item in data['tunnels']]
        return TunnelsCollection(tunnels)

    async def start_tunnel(self):
        """Makes request to POST '/api/tunnel/{name}' endpoint.
        Creates a new tunnel.
        """
        raise NotImplementedError()

    async def get_tunnel(self, name: str) -> Tunnel:
        """Gets response from GET '/api/tunnel/{name}' endpoint.
        Contains information about some particular endpoint.
        """
        url = self._url('api/tunnels/{}').format(name)
        async with self._session.get(url) as resp:
            data = await resp.json()
            if resp.status != 200:
                logging.warning(data['msg'])
                raise TunnelError(data['msg'])
        return self._make_tunnel(data)

    async def stop_tunnel(self, name: str):
        """Makes request to DELETE '/api/tunnel/{name}' endpoint.
        Stops some particular tunnel by the given name.
        """
        url = self._url('api/tunnels/{}').format(name)
        async with self._session.delete(url) as resp:
            data = await resp.json()
            if resp.status != 204:
                msg = 'unable to delete/stop tunnel'
                logging.warning(data['msg'])
                raise TunnelError(data['msg'])

    def _url(self, path: str) -> str:
        url = '{}/{}'.format(self.api_url.rstrip('/'), path.rstrip('/'))
        return url.rstrip('/')

    @staticmethod
    def _make_tunnel(item: dict) -> Tunnel:
        return Tunnel(name=item['name'],
                      uri=item['uri'],
                      proto=item['proto'],
                      public_url=item['public_url'])
