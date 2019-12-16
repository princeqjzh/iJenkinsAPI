from library.httpclient import HTTPClient
from library.constants import settings

import time

timeout = settings.get("TIMEOUT")


class IJenkins(HTTPClient):

    def __init__(self, username, password, host, port, job_name):
        """

        :param username:
        :param password:
        :param host:
        :param port:
        :param job_name:
        """
        super().__init__()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.job_name = job_name

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
        url = f'http://{self.username}:{self.password}@{self.host}:' \
              f'{self.port}/job/{self.job_name}/build'
        response = self.Post(url)
        if response.status_code < 200 or response.status_code > 206:
            raise ValueError('Response status code error for the run_build function.')

    def run_build(self):
        # Check the latest build number
        old_number = self.__get_last_build_number()

        # Start run build
        self.__run()
        print(f'Start running the job {self.job_name}')
        current_number = self.__get_last_build_number()

        # Check if the build run finished
        start = time.time()
        while not current_number > old_number:
            # wait for the latest number update
            current_number = self.__get_last_build_number()
            time.sleep(1)
            if time.time() - start >= timeout:
                raise TimeoutError('Timeout Error')

        print(f'The new build instance number is {current_number}')
        start = time.time()
        while self.__get_build_result(current_number).get('building'):
            print(f'The {job_name}\'s building is on-going .....')
            time.sleep(3)
            if time.time() - start >= timeout:
                raise TimeoutError('Timeout Error')
        result = self.__get_build_result(current_number).get('result')
        print(f'The {job_name}\'s #{current_number} building result is {result}')


if __name__ == '__main__':
    username = 'qa'
    password = '111111aA'
    host = 'localhost'
    port = '8081'
    job_name = 'TestEmail'
    client = IJenkins(username, password, host, port, job_name)
    client.run_build()
