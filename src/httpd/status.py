# 用来记录目前服务状态
# 服务状态记录在 /data/status.csv
# 目前服务状态包括列：name,type, status, lastUpdateTime,isUsing
# 其中name是项目名称，type是项目类型，status是项目状态，lastUpdateTime是最后更新时间
# 目前只有github项目，所以type都是github，name就是github项目的url的用'/'分割最后一部分
# status有：downloading, downloaded, segmenting, segmented, embedding, embedded
# isUsing是一个布尔值，用来表示是否正在使用
import os
import time
import pandas as pd

def getStatus():
    if not os.path.exists('/data/status.csv'):
        df = pd.DataFrame(columns=['name','type','status','lastUpdateTime','isUsing'])
        df.to_csv('/data/status.csv',index=False)

    df = pd.read_csv('/data/status.csv')
    return df

def setStatus(name,type,status,isUsing):
    lastUpdateTime = pd.to_datetime(time.time(),unit='s').strftime('%Y-%m-%d %H:%M:%S')
    df = getStatus()
    if name not in df['name'].tolist():
        df0 = pd.DataFrame([[name,type,status,lastUpdateTime,isUsing]],columns=['name','type','status','lastUpdateTime','isUsing'])
        df = pd.concat([df, df0], ignore_index=True)
    else:
        df.loc[(df['name'] == name)&(df['type'] == type), 'status'] = status
        df.loc[(df['name'] == name)&(df['type'] == type), 'lastUpdateTime'] = lastUpdateTime
        df.loc[(df['name'] == name)&(df['type'] == type), 'isUsing'] = isUsing
    df.to_csv('/data/status.csv',index=False)