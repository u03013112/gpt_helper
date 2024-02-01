# 从github上下载项目
import requests
import zipfile
import io
import hashlib
import os
import shutil
import threading

import sys
sys.path.append('/')
from src.httpd.status import getStatus,setStatus
from src.httpd.ProjectA import ProjectA

class DownloadFromGithub(threading.Thread):
    def __init__(self,github_url):
        super().__init__() 
        self.github_url = github_url
        self.github_url_md5 = hashlib.md5(github_url.encode()).hexdigest()
        self.name = self.github_url.split('/')[-1]
        self.tmpDir = f'/data/{self.github_url_md5}/'

        if os.path.exists(self.tmpDir):
            raise Exception("Temporary folder already exists, another download task may be in progress.")
        else:
            os.makedirs(self.tmpDir)

    def run(self):
        self.download()
        ProjectA(self.name,'github',self.tmpDir).run()
        self.done()

    def download(self):
        setStatus(self.name,'github','downloading',False)

        zip_url = self.github_url.replace('github.com', 'codeload.github.com') + '/zip/master'

        response = requests.get(zip_url)
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        zip_file.extractall(self.tmpDir)
        setStatus(self.name,'github','downloaded',False)

    def done(self):
        # 删除下载的zip文件（在此实现中，zip文件是在内存中处理的，因此无需删除）
        # 删除临时文件夹
        shutil.rmtree(self.tmpDir)

if __name__ == '__main__':
    # 使用示例：
    github_url = "https://github.com/bupticybee/elephantfish"
    downloader = DownloadFromGithub(github_url)
    downloader.start()
    downloader.join()  # 等待线程完成