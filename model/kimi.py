import requests
from loguru import logger
import yaml


class KIMI:
    def __init__(self) -> None:
        with open('/data/projects/congcong-ai/config/config.yaml', 'r', encoding='utf-8') as f:
            args = yaml.load(f.read(), Loader=yaml.FullLoader)["kimi"]
        self.chat_url = args['chat_url']
        self.upload_url = args['upload_url']
    
    def chat(self, stream, content, file_id):
        request = self.parse_request(stream, content, file_id)
        response = requests.post(url=self.chat_url, json=request)
        return response
    
    def chat_stream(self, stream, content, file_id):
        request = self.parse_request(stream, content, file_id)
        response = requests.post(url=self.chat_url, json=request, stream=True)
        for res in response.iter_lines(decode_unicode=True):
            if res:
                yield res[5:]
    
    def upload_file(self, file):
        response = requests.post(url=self.upload_url, files={"file": (file.filename, file.file)})
        logger.debug(f"文件上传结果：{response.json()}")
        if not isinstance(response.json(), dict):  # 文件上传失败
            return None
        return response.json()
    
    def parse_request(self, stream, content, file_id):
        return {
            "model": "moonshot-v1-8k",
            "messages": [{
                "content": content,
                "role": "user"
            }],
            "stream": stream,
            "file_id": file_id
        }
