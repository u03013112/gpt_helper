# gpt_helper
尝试给gpt添加参考信息

主要针对gpt记忆库以外的信息

## 参考信息

参考openai的[Embedding Wikipedia articles for search](
https://github.com/openai/openai-cookbook/blob/2c441ab9a200070fee204a63b4203628c456e878/examples/Embedding_Wikipedia_articles_for_search.ipynb#L647
)

参考openai的[Question answering using embeddings](
https://github.com/openai/openai-cookbook/blob/d891437737cf990a84fc7ac8516d615d7b65540b/examples/Question_answering_using_embeddings.ipynb#L609
)

## 主要工作
1、基础逻辑：数据收集

2、文本嵌入：然后，我们使用OpenAI的text-embedding-ada-002模型，将每个段落或小节的文本转换成一个嵌入向量，并将这些向量保存到一个CSV文件中。

3、数据加载：在需要回答问题时，我们从CSV文件中加载数据，包括每个段落或小节的文本和对应的嵌入向量。

4、问题解答：对于给定的问题，我们首先使用同样的嵌入模型将问题转换成一个嵌入向量。然后，我们在所有段落或小节的嵌入向量中找到与问题嵌入向量最相似的向量，将对应的段落或小节作为相关信息。最后，我们使用OpenAI的GPT模型，以问题和相关信息作为输入，生成问题的答案。

5、将上述部分整合成一个本地的标准api代理，方便第三方gpt client调用

## TODO
将此功能封装成gpt插件

或者将此功能做的更加灵活，内容可以随时添加或更新