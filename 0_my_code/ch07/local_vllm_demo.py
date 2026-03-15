# 7.2.2 本地模型调用 (VLLM)
'''
注意先安装 vllm 和 transformers 库：
pip install vllm transformers

在本地启动 VLLM 服务，并加载 Qwen1.5-0.5B-Chat 模型：
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen1.5-0.5B-Chat \
    --host 0.0.0.0 \
    --port 8000

服务启动后，便会在 http://localhost:8000/v1 地址上提供与 OpenAI 兼容的 API。
'''

from hello_agents import HelloAgentsLLM

llm_client = HelloAgentsLLM(
    provider="vllm",
    model="Qwen/Qwen1.5-0.5B-Chat", # 需与服务启动时指定的模型一致
    base_url="http://localhost:8000/v1",
    api_key="vllm" # 本地服务通常不需要真实API Key，可填任意非空字符串
)


llm_response = llm_client.think([{"role": "user", "content": "请介绍一下你自己。"}])

print("VLLM Response:")
for chunk in llm_response:
    #print(chunk, end="", flush=True)
    pass

