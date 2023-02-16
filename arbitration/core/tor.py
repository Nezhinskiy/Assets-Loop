import re
import subprocess
from time import sleep

import requests
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller


class Tor:
    def __init__(self):
        self.container_name: str = "infra_tor_proxy_1"
        self.container_ip: None | str = None

    def get_tor_session(self) -> requests.sessions.Session:
        """
        Set up a proxy for http and https on the running Tor host: port 9050
        and initialize the request session.
        """
        with requests.session() as session:
            session.proxies = {'http': 'socks5://tor_proxy:9050',
                               'https': 'socks5://tor_proxy:9050'}
            session.headers = {'User-Agent': UserAgent().chrome}
        return session

    def get_tor_ip(self) -> str:
        if not self.container_ip:
            cmd = f'ping -c 1 {self.container_name}'
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return re.findall(r'\(.*?\)', output)[0][1:-1]
        else:
            return self.container_ip

    def renew_connection(self) -> None:
        with Controller.from_port(address=self.get_tor_ip()) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            sleep(controller.get_newnym_wait())
