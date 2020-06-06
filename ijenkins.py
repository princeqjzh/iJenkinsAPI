from library.httpclient import HTTPClient
from library.constants import settings
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

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

    def __get_last_build_number(self):
        """ Return the latest build number of the jenkins job """

        url = f'http://{self.username}:{self.password}@{self.host}:' \
              f'{self.port}/job/{self.job_name}/lastBuild/buildNumber'
        response = self.Get(url)
        if response.status_code < 200 or response.status_code > 206:
            raise ValueError('Response status code error for the get_last_build_number function.')

        return response.text

    def __get_build_result(self, number):
        url = f'http://{self.username}:{self.password}@{self.host}:' \
              f'{self.port}/job/{self.job_name}/{number}/api/json'
        response = self.Get(url)
        if response.status_code < 200 or response.status_code > 206:
            raise ValueError('Response status code error for the get_build_status function.')
        build_result = {
            'building': response.json()['building']
            , 'result': response.json()['result']
        }
        return build_result

    def __run(self):
        jenkins_url = f'http://{self.host}:{self.port}/'
        crumb_requester = CrumbRequester(
            baseurl=jenkins_url,
            username=username,
            password=password
        )
        server = Jenkins(jenkins_url, username=username, password=password, requester=crumb_requester)
        server[job_name].invoke()

    def run_build(self):
        # Check the latest build number
        old_number = self.__get_last_build_number()

        # Start run build
        self.__run()
        self.logger.info(f'Start running the job {self.job_name}')
        current_number = self.__get_last_build_number()

        # Check if the build run finished
        start = time.time()
        while not current_number > old_number:
            # wait for the latest number update
            time.sleep(1)
            current_number = self.__get_last_build_number()
            if time.time() - start >= timeout:
                raise TimeoutError(f'Get new build number timeout Error, timeout = {timeout}')

        self.logger.info(f'The new build instance number is {current_number}')
        start = time.time()
        while self.__get_build_result(current_number).get('building'):
            self.logger.info(f'The {job_name}\'s building is on-going .....')
            time.sleep(3)
            if time.time() - start >= timeout:
                raise TimeoutError(f'Run build timeout Error, timeout = {timeout}')
        result = self.__get_build_result(current_number).get('result')
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
