# 7.2.2 本地模型调用 (Ollama)
'''
注意先在本地启动 Ollama 服务，并加载 qwen3:4b 模型
'''

from hello_agents import HelloAgentsLLM

llm_client = HelloAgentsLLM(
    provider="ollama",  # 指定使用 Ollama 作为 LLM 提供商
    model="qwen3:4b", 
    base_url="http://localhost:11434/v1", # Ollama 默认的 API 地址
    api_key="ollama" # 本地服务通常不需要真实API Key，可填任意非空字符串
)


llm_response = llm_client.think([{"role": "user", "content": "请介绍一下你自己。"}])

print("VLLM Response:")
for chunk in llm_response:
    #print(chunk, end="", flush=True)
    pass

