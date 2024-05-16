import requests


class FastGPT:
    def __init__(self) -> None:
        self.chat_url = "http://125.75.69.37:9600/api/v1/chat/completions"
        self.dataset_url = "http://125.75.69.37:9600/api/core/dataset/data/list"
        self.headers = {"Authorization": "Bearer " + "fastgpt-hBK2LavFW4ccYF2V1amhxrTxLRRclbDri5V2yxUQIvfxravX47tfJ7U"}

    def chat(self, chat_id, stream, content):
        request = self.parse_chat_request(chat_id, stream, content)
        response = requests.post(url=self.chat_url, json=request, headers=self.headers)
        return response
    
    def chat_stream(self, chat_id, stream, content):
        request = self.parse_chat_request(chat_id, stream, content)
        response = requests.post(url=self.chat_url, json=request, headers=self.headers, stream=True)
        for res in response.iter_lines(decode_unicode=True):
            if res:
                yield res[5:]

    def parse_chat_request(self, chat_id, stream, content):
        return {
            "chatId": chat_id,
            "stream": stream,
            "detail": False,
            "messages": [{
                "content": content,
                "role": "user"
            }]
        }

    def dataset(self, request):
        request = self.parse_dataset_request(request)
        response = requests.post(url=self.dataset_url, json=request, headers=self.headers)
        return response
    
    def parse_dataset_request(self, raw_request):
        return {
            "pageNum": raw_request.page_num,
            "pageSize": raw_request.page_size,
            "collectionId": raw_request.collection_id,
            "searchText": raw_request.search_text
        }
