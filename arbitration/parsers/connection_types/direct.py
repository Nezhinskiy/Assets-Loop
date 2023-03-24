import time

import requests


class Direct:
    """
    A class for direct connection to make HTTP requests using the requests
    library.
    Attributes:
        request_timeout (int): The timeout value for HTTP requests.
    """
    request_timeout: int = 5

    def __init__(self) -> None:
        """
        Initializes a Direct object and creates a session object.
        """
        self.session: requests.sessions.Session = self.__set_direct_session()

    @staticmethod
    def __set_direct_session() -> requests.sessions.Session:
        """
        Static method that creates and returns a session object for the Direct
        object.
        """
        return requests.session()

    def renew_connection(self) -> None:
        """
        Placeholder method that will be used to renew the HTTP connection.
        """
        time.sleep(2)
