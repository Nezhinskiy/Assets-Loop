from typing import Any, Dict

import requests


class Cookie:
    """
    This class represents a set of cookies that can be added to the headers of
    HTTP requests made using a requests session object.

    Attributes:
        endpoint (str): The URL of the endpoint that will be requested to
            obtain the cookies.
        session (requests.sessions.Session): A requests session object to use
            for making HTTP requests.
        cookies (dict): Cookies in the form of a dictionary.
        cookies_names (Optional[Iterable[str]]): An optional iterable of cookie
            names to include in the headers. If not provided, all cookies
            obtained from the endpoint will be included.
    """
    def __init__(self, endpoint: str, session: requests.sessions.Session,
                 cookies_names=None) -> None:
        """
        Initializes a new Cookie instance by obtaining the cookies from the
        specified endpoint using the provided session object. If cookies_names
        is not provided, all cookies obtained will be used.
        """
        self.endpoint: str = endpoint
        self.session: requests.sessions.Session = session
        self.cookies: Dict[str, Any] = self.__get_cookies()
        self.cookies_names: str = cookies_names or self.cookies.keys()

    def __get_cookies(self) -> Dict[str, Any]:
        """
        Private method that obtains the cookies from the endpoint using the
        session object and returns them as a dictionary.
        """
        self.session.get(self.endpoint)
        return self.session.cookies.get_dict()

    def add_cookies_to_headers(self) -> None:
        """
        Adds the cookies to the headers of the session object by updating the
        'Cookie' field in the headers dictionary with the values of the
        specified cookie names.
        """
        headers_with_cookies = {
            'Cookie': '; '.join(
                [f'{name}={self.cookies[name]}' for name in self.cookies_names]
            )
        }
        self.session.headers.update(headers_with_cookies)
