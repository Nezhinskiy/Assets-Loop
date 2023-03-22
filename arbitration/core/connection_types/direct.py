import requests


class Direct:
    request_timeout: int = 2

    def __init__(self, waiting_time=10) -> None:
        self.waiting_time: int = waiting_time
        self.session: requests.sessions.Session = self.__set_direct_session()

    @staticmethod
    def __set_direct_session() -> requests.sessions.Session:
        return requests.session()

    def renew_connection(self) -> None:
        pass
