from typing import List

import requests
from fp.fp import FreeProxy

from arbitration.settings import COUNTRIES_NEAR_SERVER


class Proxy:
    """
    A class to manage proxy connections for making HTTP requests.

    Attributes:
        request_timeout (int): The timeout value for HTTP requests.
        country_id (List[str]): A list of country codes to limit proxy
            selection to.
    """
    request_timeout: int = 4
    country_id: List[str] = COUNTRIES_NEAR_SERVER

    def __init__(self) -> None:
        """
        Initializes the Proxy class and sets up a new session with a proxy.
        """
        self.proxy_list = FreeProxy(country_id=self.country_id, elite=True)
        self.proxy_url: str = self.__set_proxy_url()
        self.session: requests.sessions.Session = self.__set_proxy_session()

    def __set_proxy_session(self) -> requests.sessions.Session:
        """
        Private method to set up a new requests session with the currently
        selected proxy.
        """
        with requests.session() as session:
            session.proxies = {'http': self.proxy_url}
            return session

    def __set_proxy_url(self) -> str:
        """
        Private method to get a new proxy URL from the proxy list.
        """
        return self.proxy_list.get()

    def renew_connection(self) -> None:
        """
        Public method to renew the proxy connection by getting a new proxy URL
        and setting up a new session.
        """
        self.proxy_url = self.__set_proxy_url()
        self.session = self.__set_proxy_session()
