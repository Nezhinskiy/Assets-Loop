from typing import Any, Dict

import requests


class Cookie:
    def __init__(self, endpoint: str, session: requests.sessions.Session,
                 cookies_names=None) -> None:
        self.endpoint = endpoint
        self.session = session
        self.cookies = self.__get_cookies()
        self.cookies_names = cookies_names or self.cookies.keys()

    def __get_cookies(self) -> Dict[str, Any]:
        self.session.get(self.endpoint)
        return self.session.cookies.get_dict()

    def add_cookies_to_headers(self) -> None:
        headers_with_cookies = {
            'Cookie': '; '.join(
                [f"{name}={self.cookies[name]}" for name in self.cookies_names]
            )
        }
        self.session.headers.update(headers_with_cookies)
