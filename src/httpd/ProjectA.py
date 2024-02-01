# 项目处理，对于下载完成的项目，进行分段和向量化处理
import os
import pandas as pd

import sys
sys.path.append('/')
from src.SegmentPyFile import SegmentPyFile
from src.tools import embed
from src.httpd.status import getStatus,setStatus


class ProjectA():
    def __init__(self,name,type,dir) -> None:
        self.name = name
        self.type = type
        self.dir = dir
    
    def segment(self):
        setStatus(self.name,self.type,'segmenting',False)
        # TODO:暂时只能解析python文件
        pySegDf = pd.DataFrame()
        
        for root, dirs, files in os.walk(self.dir):
            for file in files:
                if file.endswith('.py'):
                    filename = os.path.join(root, file)
                    print('segment file:',filename)
                    seg = SegmentPyFile(filename)
        
                    df = seg.seg(maxToken=1000)
                    pySegDf = pd.concat([pySegDf, df], ignore_index=True)

        # 实测这种import代码对代码理解作用小，暂时去掉，效果貌似更好
        pySegDf = pySegDf[pySegDf['codeType'] != 'Import']
        pySegDf = pySegDf[pySegDf['codeType'] != 'ImportFrom']

        pySegDf.to_csv(f'/data/segment/{self.name}_{self.type}.csv', index=False)

        # 对python部分text整合，将代码的属性和内容放在一起，方便向量化。
        textList = []
        for index, row in pySegDf.iterrows():
            textList.append(f'''
代码路径:{row['codePath']}
代码所在行号:{row['startLineNo']}
代码类型:{row['codeType']}
代码内容:{row['codeContent']}
        ''')

        setStatus(self.name,self.type,'segmented',False)
        return textList
    
    def embed(self,textList):
        setStatus(self.name,self.type,'embedding',False)
        embedDf = embed(textList)
        setStatus(self.name,self.type,'embedded',False)
        return embedDf
    
    def run(self):
        textList = self.segment()
        embedDf = self.embed(textList)
        embedDf.to_csv(f'/data/embedded/{self.name}_{self.type}.csv', index=False)
        return 