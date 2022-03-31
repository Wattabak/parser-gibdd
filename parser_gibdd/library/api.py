import enum
import logging
import warnings
from datetime import datetime
from typing import Optional, List, Dict

from requests import PreparedRequest
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ConnectionError
from urllib3.exceptions import NewConnectionError, ConnectTimeoutError


class ProxyStatus(int, enum.Enum):
    unknown = enum.auto()
    available = enum.auto()
    unavailable = enum.auto()


class ProxyType(str, enum.Enum):
    HTTP = 'http'
    HTTPS = 'https'
    SOCKS5 = 'socks5'


class Proxy:

    def __init__(self,
                 url: str,
                 updated_at: Optional[datetime] = None,
                 status: Optional[ProxyStatus] = None,
                 ):
        self.url = url
        self.updated_at = datetime.now() if not updated_at else updated_at
        self.status = ProxyStatus.unknown if not status else status
        self.type = self.get_proxy_type(url)

    def get_proxy_type(self, url: str):
        if 'socks5://' in url:
            return ProxyType.SOCKS5
        elif 'https://' in url:
            return ProxyType.HTTPS
        else:
            return ProxyType.HTTP


class RotatingProxyList:
    _current_proxies = {
        'http': None,
        'https': None
    }

    def __init__(self, proxies: List[str] = None):
        self._proxies = self.normalize_proxies(proxies)
        self.resolve_proxies()

    @property
    def current_proxies(self) -> Dict[str, Optional[str]]:
        return self._current_proxies

    def normalize_proxies(self, proxies: List[str]) -> Dict[str, Proxy]:
        return {
            proxy: Proxy(url=proxy)
            for proxy in proxies
        }

    def resolve_proxies(self):
        current_http_proxy = next((
            url
            for url, proxy in self._proxies.items()
            if proxy.type in [ProxyType.HTTP, ProxyType.SOCKS5] \
               and proxy.status <= ProxyStatus.available
        ), None)
        current_https_proxy = next((
            url
            for url, proxy in self._proxies.items()
            if proxy.type in [ProxyType.HTTPS, ProxyType.SOCKS5] \
               and proxy.status <= ProxyStatus.available
        ), None)
        if not any((current_https_proxy, current_http_proxy)):
            warnings.warn('No available proxies, reverting to using simple requests')
        logging.info([current_https_proxy, current_http_proxy])
        self._current_proxies['http'] = current_http_proxy
        self._current_proxies['https'] = current_https_proxy

    def __get__(self, instance, owner):
        return self._current_proxies

    def __set__(self, instance, value: str):
        self._proxies.update(self.normalize_proxies([value]))

    def __repr__(self):
        return self._current_proxies

    def rotate(self, new_status: ProxyStatus):
        http = self._current_proxies['http']
        if not http:
            self._proxies[self._current_proxies['https']].status = new_status
        else:
            self._proxies[self._current_proxies['http']].status = new_status
        self.resolve_proxies()


class ProxyRotatingAdapter(HTTPAdapter):

    def __init__(self,
                 *args,
                 available_proxies: List[str],
                 **kwargs,
                 ):
        super(ProxyRotatingAdapter, self).__init__(*args, **kwargs)
        self.available_proxies: RotatingProxyList = RotatingProxyList(available_proxies)

    def send(
            self,
            request: PreparedRequest,
            *args,
            **kwargs,
    ) -> Response:
        settings = {
            'proxies': self.available_proxies.current_proxies,
            'timeout': 3,
        }
        try:
            kwargs.update(settings)
            return super().send(request,
                                *args,
                                **kwargs,
                                )
        except (ProxyError, ConnectionError, NewConnectionError, ConnectTimeoutError) as e:
            logging.exception(f'Encountered a proxy error, rotating proxy, {type(e)}')
            self.available_proxies.rotate(new_status=ProxyStatus.unavailable)
            kwargs.update(settings)
            return self.send(request, *args, **kwargs, )
