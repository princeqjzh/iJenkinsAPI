from library.httpclient import HTTPClient
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
from library.constants import settings

import logging
import time
import os
import configparser

timeout = settings.get("TIMEOUT")


class IJenkins(HTTPClient):

    def __init__(self, username, password, host, port, job_name):
        """
        Jenkins API Client Side Caller
        :param username: Jenkins username, with job running permission (str)
        :param password: Jenkins password (str)
        :param host: Jenkins Server hostname or IP address (str)
        :param port: Jenkins Server port (str)
        :param job_name: Job name (str)
        """
        super().__init__()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.job_name = job_name
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S')
        self.logger = logging.getLogger()
        jenkins_url = f'http://{self.host}:{self.port}/'
        crumb_requester = CrumbRequester(
            baseurl=jenkins_url,
            username=username,
            password=password
        )
        self.server_api = Jenkins(jenkins_url, username=username, password=password, requester=crumb_requester)

    def get_last_build_number(self):
        """ Return the latest build number of the jenkins job """

        return self.server_api[self.job_name].get_last_build().get_number()

    def get_build_result(self, number):

        return self.server_api[self.job_name].get_build(number)

    def run(self):
        self.server_api[self.job_name].invoke()

    def run_build(self):
        # Check the latest build number
        old_number = self.get_last_build_number()

        # Start run build
        self.run()
        self.logger.info(f'Start running the job {self.job_name}')
        current_number = self.get_last_build_number()

        # Check if the build run finished
        start = time.time()
        while not current_number > old_number:
            # wait for the latest number update
            time.sleep(1)
            current_number = self.get_last_build_number()
            if time.time() - start >= settings['TIMEOUT']:
                raise TimeoutError(f'Get new build number timeout Error, timeout = {settings["TIMEOUT"]}')

        self.logger.info(f'The new build instance number is {current_number}')
        start = time.time()
        while self.get_build_result(current_number).is_running():
            self.logger.info(f'The {job_name}\'s building is on-going .....')
            time.sleep(settings['POLLING'])
            if time.time() - start >= timeout:
                raise TimeoutError(f'Run build timeout Error, timeout = {settings["TIMEOUT"]}')
        result = self.get_build_result(current_number).get_status()
        self.logger.info(f'The {job_name}\'s #{current_number} building result is {result}')


def get_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.environ['HOME'], 'ijenkins_config.ini'))
    return config


if __name__ == '__main__':
    config = get_config()
    username = config.get('jenkins', 'username')
    password = config.get('jenkins', 'password')
    host = config.get('jenkins', 'host')
    port = config.get('jenkins', 'port')
    job_name = config.get('jenkins', 'job_name')

    client = IJenkins(username, password, host, port, job_name)
    client.run_build()
