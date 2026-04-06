import requests


class LLMClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.deepseek.com/v1/chat/completions"

    def chat_stream(self, user_message, system_message="你是一个有用的助手", temperature=0.7):
        """流式调用，一个字一个字返回"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "stream": True  # 这行是关键：开启流式输出
        }

        response = requests.post(self.url, headers=headers, json=data, stream=True)

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    import json
                    chunk = json.loads(data_str)
                    delta = chunk.get('choices', [{}])[0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        yield content  # 每次返回一个字