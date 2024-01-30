# 一般的工具，抽象到这里
import tiktoken

# 计算token
def num_tokens(text: str, model: str = 'gpt-4') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

if __name__ == '__main__':
    print(num_tokens('中国是否有参加2022冬奥会？',model='gpt-4'))
    
