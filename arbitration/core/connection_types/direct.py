import time
from datetime import datetime, timezone

import requests


class Direct:
    request_timeout: int = 3
    connection_time: float
    renew_connection_time: float

    def __init__(self, waiting_time=10) -> None:
        self.waiting_time: int = waiting_time
        self.session: requests.sessions.Session = self.__set_direct_session()

    def __set_direct_session(self) -> requests.sessions.Session:
        start_time = datetime.now(timezone.utc)
        with requests.session() as session:
            self.connection_time = (datetime.now(timezone.utc) - start_time
                                    ).seconds
            return session

    def renew_connection(self) -> None:
        time.sleep(self.waiting_time)
        self.renew_connection_time = self.waiting_time
