# python代码分段
import sys
sys.path.append('/src')
from tools import num_tokens

import ast
import pandas as pd

# 输入文件完整路径
# 输出分好段的代码，用一个DataFrame表示
# 每一段代码一行，列：代码路径，代码开始行号，代码类型，代码内容
# 其中代码路径是文件内的路径，即当一段代码过长时，会递归调用本函数，将代码再分段。而代码在分段时要将代码结构进行记录。
# 用ast实现
# 大致输出结论：
# 代码路径： class C -> func1 ,代码开始行号：100，代码类型： function，代码内容： def func1(): pass

class SegmentPyFile():
    def __init__(self,filename) -> None:
        with open(filename,'r') as f:
            self.code = f.read()
            self.prefix = '->'.join(filename.split('/')[1:])

    def seg(self, node=None, prefix='', maxToken=100):
        if node is None:
            node = ast.parse(self.code)
            prefix = self.prefix

        codePathList = []
        startLineNoList = []
        codeTypeList = []
        codeContentList = []
        tokenCountList = []

        for child in ast.iter_child_nodes(node):
            if not hasattr(child, 'lineno'):
                continue

            newPrefix = f"{prefix} -> {child.__class__.__name__}"
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                newPrefix = f"{prefix} -> {child.__class__.__name__} {child.name}"

            codeContent = self.code.split('\n')[child.lineno - 1:child.end_lineno]
            codeContentStr = '\n'.join(codeContent)
            tokenCount = num_tokens(codeContentStr)
            if tokenCount <= maxToken:
                codePathList.append(newPrefix)
                startLineNoList.append(child.lineno)
                codeTypeList.append(child.__class__.__name__)
                codeContentList.append(codeContent)
                tokenCountList.append(tokenCount)
            else:
                has_children = False
                for subchild in ast.iter_child_nodes(child):
                    if not hasattr(subchild, 'lineno'):
                        continue
                    has_children = True
                    codeContent = self.code.split('\n')[child.lineno - 1:subchild.lineno - 1]
                    codeContentStr = '\n'.join(codeContent)
                    tokenCount = num_tokens(codeContentStr)
                    if tokenCount <= maxToken:
                        codePathList.append(newPrefix)
                        startLineNoList.append(child.lineno)
                        codeTypeList.append(child.__class__.__name__)
                        codeContentList.append(codeContent)
                        tokenCountList.append(tokenCount)
                    break
                if not has_children:
                    print(f"第{child.lineno}行的 {child.__class__.__name__} 代码（名字：{getattr(child, 'name', '')}），token数量 {tokenCount}，无法再次细分，请注意。")
                    continue

                child_df = self.seg(child, newPrefix, maxToken)
                codePathList.extend(child_df['codePath'].tolist())
                startLineNoList.extend(child_df['startLineNo'].tolist())
                codeTypeList.extend(child_df['codeType'].tolist())
                codeContentList.extend(child_df['codeContent'].tolist())
                tokenCountList.extend(child_df['tokenCount'].tolist())

        return pd.DataFrame({
            'codePath': codePathList,
            'startLineNo': startLineNoList,
            'codeType': codeTypeList,
            'codeContent': codeContentList,
            'tokenCount': tokenCountList
        })
    
import os
if __name__ == '__main__':
    srcDir = '/src'
    
    srcDf = pd.DataFrame()

    for root, dirs, files in os.walk(srcDir):
        for file in files:
            if file.endswith('.py'):
                filename = os.path.join(root, file)
                print('segment file:',filename)
                seg = SegmentPyFile(filename)
    
                df = seg.seg(maxToken=500)

                # srcDf = srcDf.append(df)
                # df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                srcDf = pd.concat([srcDf, df], ignore_index=True)

    srcDf.to_csv('/data/segmentedCode_src.csv', index=False)
    
