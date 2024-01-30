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

class PyCodeSeg():
    def __init__(self,filename) -> None:
        with open(filename,'r') as f:
            self.code = f.read()
            self.df = pd.DataFrame(columns=['codePath', 'startLineNo', 'codeType', 'codeContent'])

    def seg(self, node=None, prefix='', maxToken=100):
        if node is None:
            node = ast.parse(self.code)

        codePathList = []
        startLineNoList = []
        codeTypeList = []
        codeContentList = []
        tokenCountList = []

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                newPrefix = f"{prefix} -> {child.name}"
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
    
if __name__ == '__main__':
    seg = PyCodeSeg('askDemo.py')
    df = seg.seg(maxToken=500)
    print(df)

    # TODO: 代码分段不完整，声明、import都没看到，还不知道有什么其他不完整部分
    # TODO：代码细分之后最小的代码段，还是有很多token，即没有child了，这个时候应该怎么办？
    # TODO: 代码分段之后，父节点被忽略了，至少要有父节点的一些内容，比如class的定义
    # TODO：代码再修正，可以直接读取文件夹