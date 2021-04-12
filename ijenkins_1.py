from library.httpclient import HTTPClient
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

import logging
import time

timeout = 60
polling = 3


class IJenkins(HTTPClient):

    def __init__(self, username, password, host, port, job_name):
        """ Jenkins API 初始化

        :param username: Jenkins 用户名，拥有执行任务的权限 (str)
        :param password: Jenkins 密码 (str)
        :param host: Jenkins 服务 hostname 或者 IP 地址 (str)
        :param port: Jenkins 服务端口 (str)
        :param job_name: 任务名 (str)
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

    def get_last_build_number(self):
        """ 返回最新构建编号

        :return 最新构建编号(int)
        """

        return self.jenkins_api[self.job_name].get_last_build().get_number()

    def get_build_obj(self, number):
        """ 返回对应编号的构建对象实例。

        :param number: 构建编号(int)
        :return : 构建对象 (build)
        """

        return self.jenkins_api[self.job_name].get_build(number)

    def run(self):
        """ 运行任务 """

        self.jenkins_api[self.job_name].invoke()

    def run_build(self):
        """ 运行构建任务"""

        # 获取最新构建编号
        old_number = self.get_last_build_number()

        # 运行构建
        self.run()
        self.logger.info(f'Start running the job {self.job_name}')
        current_number = self.get_last_build_number()

        # 检查构建运行是否完成
        start = time.time()
        while not current_number > old_number:
            # 等待最新构建编号更新
            time.sleep(1)
            current_number = self.get_last_build_number()
            if time.time() - start >= timeout:
                raise TimeoutError(f'Get new build number timeout Error, timeout = {timeout}')

        self.logger.info(f'The new build instance number is {current_number}')
        start = time.time()
        while self.get_build_obj(current_number).is_running():
            self.logger.info(f'The {self.job_name}\'s building is on-going .....')
            time.sleep(polling)
            if time.time() - start >= timeout:
                raise TimeoutError(f'Run build timeout Error, timeout = {timeout}')
        result = self.get_build_obj(current_number).get_status()
        self.logger.info(f'The {self.job_name}\'s #{current_number} building result is {result}')


if __name__ == '__main__':

    client = IJenkins('qa', '123456', 'k8s.testing-studio.com', '9111', 'Test1')
    client.run_build()
