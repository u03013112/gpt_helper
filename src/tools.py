# 一般的工具，抽象到这里
import sys
sys.path.append('/')
from src.config import openaiApiKey,openaiUrl,openaiEmbeddingsUrl

import openai
import pandas as pd
import tiktoken

# 计算token
def num_tokens(text: str, model: str = 'gpt-4') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


embeddingsClient = openai.AzureOpenAI(
    azure_endpoint=openaiEmbeddingsUrl,
    api_key=openaiApiKey,
    api_version="2023-07-01-preview"
)

client = openai.AzureOpenAI(
    azure_endpoint=openaiUrl,
    api_key=openaiApiKey,
    api_version="2023-07-01-preview"
)

# 批量向量化,其中textList是一个list，每个元素是一个str，数量可以大于batchSize
# 返回DataFrame，列：text,embedding
def embed(textList,batchSize = 1000):
    embeddings = []
    for batchStart in range(0,len(textList),batchSize):
        batchEnd = batchStart + batchSize
        batch = textList[batchStart:batchEnd]
        print(f'Batch {batchStart} to {batchEnd}')
        response = embeddingsClient.embeddings.create(model='text-embedding-ada-002', input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)
    
    df = pd.DataFrame({"text": textList, "embedding": embeddings})
    return df


if __name__ == '__main__':
    print(num_tokens('中国是否有参加2022冬奥会？',model='gpt-4'))
    
