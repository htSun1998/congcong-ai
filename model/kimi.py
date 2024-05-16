import requests


class KIMI:
    def __init__(self) -> None:
        self.chat_url = "http://36.103.239.194:7869/v1/chat/completions"
        self.upload_url = "http://36.103.239.194:7869/create"
    
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
