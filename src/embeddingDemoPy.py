# 尝试对代码进行embedding
import ast
import pandas as pd
import sys
sys.path.append('/')
from src.tools import num_tokens,embed,embeddingsClient,client
from scipy import spatial

def embedding():
    df = pd.read_csv('/data/segmentedCode_src.csv')
    # 进行一些过滤，codeType:Import 
    df = df[df['codeType'] != 'Import']
    df = df[df['codeType'] != 'ImportFrom']

    # 将 codePath,startLineNo,codeType,codeContent 合并成一个字符串
    # 按照格式：'codePath':codePath + '\n' + 'startLineNo':startLineNo + '\n' + 'codeType':codeType + '\n' + 'codeContent':codeContent
    # 变为一个字符串列表
    textList = []
    for index, row in df.iterrows():
        textList.append(f'''
codePath:{row['codePath']}
startLineNo:{row['startLineNo']}
codeType:{row['codeType']}
codeContent:{row['codeContent']}
        ''')
    # print(textList[0])
    df = embed(textList)
    df.to_csv('/data/embeddedCode_src.csv', index=False)

def strings_ranked_by_relatedness(
        query: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 100
    ) -> tuple[list[str], list[float]]:
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        query_embedding_response = embeddingsClient.embeddings.create(
            model="text-embedding-ada-002",
            input=query,
        )
        query_embedding = query_embedding_response.data[0].embedding
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        return strings[:top_n], relatednesses[:top_n]

# def query_message(
#         query: str,
#         df: pd.DataFrame,
#         token_budget: int
#     ) -> str:
#         """Return a message for GPT, with relevant source texts pulled from a dataframe."""
#         strings, relatednesses = strings_ranked_by_relatedness(query, df)
#         introduction = '下面是有关GPT_HELPER的代码片段，如果问到相关问题，请参阅下面的代码片段。如果代码片段中没有答案，请写“我找不到答案。”'
#         question = f"\n\nQuestion: {query}"
#         message = introduction
#         for string in strings:
#             next_article = f'\n\n代码片段:\n"""\n{string}\n"""'
#             if (
#                 num_tokens(message + next_article + question)
#                 > token_budget
#             ):
#                 break
#             else:
#                 message += next_article
#         return message + question

def query_message(
        query: str,
        df: pd.DataFrame,
        token_budget: int,
        max_articles: int
    ) -> str:
        """Return a message for GPT, with relevant source texts pulled from a dataframe."""
        strings, relatednesses = strings_ranked_by_relatedness(query, df)
        introduction = '下面是有关GPT_HELPER的代码片段，如果问到相关问题，请参阅下面的代码片段。如果代码片段中没有答案，请写“我找不到答案。”'
        question = f"\n\nQuestion: {query}"
        message = introduction
        article_count = 0
        for string in strings:
            if article_count >= max_articles:
                break
            next_article = f'\n\n代码片段:\n"""\n{string}\n"""'
            if (
                num_tokens(message + next_article + question)
                > token_budget
            ):
                break
            else:
                message += next_article
                article_count += 1
        return message + question
    
def ask(
        query: str,
        model: str = 'bigpt4',
        token_budget: int = 1024*7 - 500,
        print_message: bool = False,
        df: pd.DataFrame = None
    ) -> str:
        """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
        message = query_message(query, df, token_budget=token_budget,max_articles=10)

        if print_message:
            print(message)
        messages = [
            {"role": "user", "content": message},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        response_message = response.choices[0].message.content

        print(response_message)
        return response_message
    
def debug():
    df = pd.read_csv('/data/segmentedCode_src.csv')
    df = df[df['codeType'] != 'Import']
    df = df[df['codeType'] != 'ImportFrom']

    print(df)

if __name__ == '__main__':
    embedding()

    df = pd.read_csv('/data/embeddedCode_src.csv')
    df['embedding'] = df['embedding'].apply(ast.literal_eval)

    questions = [
        # 'SegmentPyFile.py 这个文件主要功能，和主要步骤，如果有必要可以将重要的代码片段贴出来',
        'httpd.py 这个文件主要功能。代码是否有问题，有什么可以改进的地方',
        # 'query_message 这个方法是在想定的token中尽可能的插入参考数据，我觉得插入太多的参考数据没有价值，所以做限定，给这个方法添加一个参数N，即在token足够的情况下，最多插入N条数据，再多就不要了。帮我重写一下这个方法',
    ]

    for question in questions:
        print('question:',question)
        ask(question,df = df)

    
     
    # debug()
