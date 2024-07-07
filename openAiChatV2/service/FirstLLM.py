from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model='deepseek-chat',
    api_key='sk-0da03bdfd5414766ae05a0050134cfb1',
    base_url='https://api.deepseek.com',
    max_tokens=1024
)

response = llm.invoke("Hi!")
print(response)