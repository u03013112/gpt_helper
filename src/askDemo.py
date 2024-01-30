# imports
import ast  # for converting embeddings saved as strings back to arrays
import openai
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search
import time

import sys
sys.path.append('/')
from src.config import openaiApiKey,openaiUrl,openaiEmbeddingsUrl

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


# # examples
# strings, relatednesses = strings_ranked_by_relatedness("curling gold medal", df, top_n=5)
# for string, relatedness in zip(strings, relatednesses):
#     print(f"{relatedness=:.3f}")
#     print(string)

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))



# ask('Which athletes won the gold medal in curling at the 2022 Winter Olympics?',model='bigpt4')

# ask('中国是否有参加2022冬奥会？',model='bigpt4')

# ask('中国在2022冬奥会表现怎么样，主要从金牌总数，奖牌总数，和金牌总数国家排名，奖牌总数国家排名来说说。',model='bigpt4')


class askFor2022WinterOlympics():
    def __init__(self):
        embeddings_path = "/data/winter_olympics_2022.csv"
        df = pd.read_csv(embeddings_path)
        df['embedding'] = df['embedding'].apply(ast.literal_eval)
        self.df = df

        self.client = openai.AzureOpenAI(
            azure_endpoint=openaiUrl,
            api_key=openaiApiKey,
            api_version="2023-07-01-preview"
        )

        self.embeddingsClient = openai.AzureOpenAI(
            azure_endpoint=openaiEmbeddingsUrl,
            api_key=openaiApiKey,
            api_version="2023-07-01-preview"
        )

    def strings_ranked_by_relatedness(self,
        query: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 100
    ) -> tuple[list[str], list[float]]:
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        query_embedding_response = self.embeddingsClient.embeddings.create(
            model=EMBEDDING_MODEL,
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

    def query_message(self,
        query: str,
        df: pd.DataFrame,
        model: str,
        token_budget: int
    ) -> str:
        """Return a message for GPT, with relevant source texts pulled from a dataframe."""
        strings, relatednesses = self.strings_ranked_by_relatedness(query, df)
        # introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
        introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
        question = f"\n\nQuestion: {query}"
        message = introduction
        for string in strings:
            next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
            if (
                num_tokens(message + next_article + question, model=model)
                > token_budget
            ):
                break
            else:
                message += next_article
        return message + question

    def ask(self,
        query: str,
        model: str = 'bigpt4',
        token_budget: int = 1024*7 - 500,
        print_message: bool = False,
    ) -> str:
        t0 = time.time()

        """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
        message = self.query_message(query, self.df, model=GPT_MODEL, token_budget=token_budget)

        print(f"Time to generate message: {time.time() - t0:.2f} seconds")

        if print_message:
            print(message)
        messages = [
            {"role": "system", "content": "You answer questions about the 2022 Winter Olympics."},
            {"role": "user", "content": message},
        ]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        response_message = response.choices[0].message.content

        print(f"Time to generate response: {time.time() - t0:.2f} seconds")

        print(response_message)
        return response_message
    
    def query_message2(self,
        query: str,
        df: pd.DataFrame,
        model: str,
        token_budget: int
    ) -> str:
        """Return a message for GPT, with relevant source texts pulled from a dataframe."""
        strings, relatednesses = self.strings_ranked_by_relatedness(query, df)
        # introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
        introduction = '下面是一些有关2022年冬奥会的文章，如果你用的上可以参考这些，如果用不上请忽略这部分内容，专注于聊天内容。'
        question = f"\n\nQuestion: {query}"
        message = introduction
        for string in strings:
            next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
            if (
                num_tokens(message + next_article + question, model=model)
                > token_budget
            ):
                break
            else:
                message += next_article
        return message



    # 与ask区别：输入是messages，类似：[{"role": "user", "content": "Which athletes won the gold medal in curling at the 2022 Winter Olympics?"}]
    def ask2(self,messages,model='bigpt4',token_budget: int = 1024*4 - 500,
        print_message: bool = False) -> str:
        # 先找到最后一个user的message
        lastUserMessage = ''
        for message in messages:
            if message['role'] == 'user':
                lastUserMessage = message['content']

        print('lastUserMessage:',lastUserMessage)
        message = self.query_message2(lastUserMessage, self.df, model=GPT_MODEL, token_budget=token_budget)

        messages.insert(0,{"role": "user", "content": message})
        if print_message:
            print(messages)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        response_message = response.choices[0].message.content
        print(response_message)
        return response_message
    

if __name__ == "__main__":
    startTime = time.time()
    askFor2022WinterOlympics = askFor2022WinterOlympics()
    print('init time:',time.time()-startTime)

    askFor2022WinterOlympics.ask('Which athletes won the gold medal in curling at the 2022 Winter Olympics?',model='bigpt4')


    askFor2022WinterOlympics.ask('中国是否有参加2022冬奥会？',model='bigpt4')
    askFor2022WinterOlympics.ask('中国在2022冬奥会表现怎么样，主要从金牌总数，奖牌总数，和金牌总数国家排名，奖牌总数国家排名来说说。',model='bigpt4')