from library.httpclient import HTTPClient
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

import logging
import time

timeout = 60
polling = 3


class IJenkins(HTTPClient):

    def __init__(self, username, password, host, port, job_name):
        """  Jenkins API Client Side Caller

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
        self.jenkins_api = Jenkins(jenkins_url, requester=crumb_requester)

    def __get_last_build_number(self):
        """ Return the latest build number of the jenkins job """

        return self.jenkins_api[self.job_name].get_last_build().get_number()

    def __get_build_result(self, number):

        return self.jenkins_api[self.job_name].get_build(number)

    def __run(self):
        self.jenkins_api[self.job_name].invoke()

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
        while self.__get_build_result(current_number).is_running():
            self.logger.info(f'The {self.job_name}\'s building is on-going .....')
            time.sleep(polling)
            if time.time() - start >= timeout:
                raise TimeoutError(f'Run build timeout Error, timeout = {timeout}')
        result = self.__get_build_result(current_number).get_status()
        self.logger.info(f'The {self.job_name}\'s #{current_number} building result is {result}')


if __name__ == '__main__':

    client = IJenkins('qa', '123456', 'localhost', '8081', 'TestEmail')
    client.run_build()
