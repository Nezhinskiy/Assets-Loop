from datetime import datetime, timezone
from typing import List

import requests
from fp.fp import FreeProxy

from arbitration.settings import COUNTRIES_NEAR_SERVER


class Proxy:
    request_timeout: int = 3
    connection_time: float
    renew_connection_time: float
    country_id: List[str] = COUNTRIES_NEAR_SERVER

    def __init__(self) -> None:
        self.proxy_list = FreeProxy(country_id=self.country_id, elite=True)
        self.proxy_url: str = self.__set_proxy_url()
        self.session: requests.sessions.Session = self.__set_proxy_session()

    def __set_proxy_session(self) -> requests.sessions.Session:
        start_time = datetime.now(timezone.utc)
        with requests.session() as session:
            session.proxies = {'http': self.proxy_url}
            self.connection_time = (datetime.now(timezone.utc) - start_time
                                    ).seconds
            return session

    def __set_proxy_url(self) -> str:
        return self.proxy_list.get()

    def renew_connection(self) -> None:
        start_time = datetime.now(timezone.utc)
        self.proxy_url = self.__set_proxy_url()
        self.session = self.__set_proxy_session()
        self.renew_connection_time = (datetime.now(timezone.utc) - start_time
                                      ).seconds
