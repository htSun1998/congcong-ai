import requests
from sse_starlette import ServerSentEvent
import json
import asyncio
from random import random
import time


class FastGPT:
    def __init__(self) -> None:
        self.chat_url = "http://125.75.69.37:9600/api/v1/chat/completions"
        self.dataset_url = "http://125.75.69.37:9600/api/core/dataset/data/list"
        self.headers = {"Authorization": "Bearer " +
                        "fastgpt-dIQ2JPppJT5T9tg7eF0tH1MhUsU8ygpN9ZCokMyMmWFuOPNlop9vJB4BcLBF1v"}

    def chat(self, chat_id, stream, content):
        request = self.parse_chat_request(
            chat_id, stream, content, detail=False)
        response = requests.post(
            url=self.chat_url, json=request, headers=self.headers)
        return response

    def chat_stream(self, chat_id, stream, content):
        request = self.parse_chat_request(
            chat_id, stream, content, detail=True)
        response = requests.post(
            url=self.chat_url, json=request, headers=self.headers, stream=True)
        stream_iterator = response.iter_lines(decode_unicode=True)
        while True:
            item: str | None = next(stream_iterator, None)
            if item is None:  # 结束
                break
            if item == "":  # 空行
                continue
            if item.endswith("fastAnswer"):  # 直接回答，网络搜索结果
                item = next(stream_iterator)
                web_stream_iterator = self.web_stream(item)
                for web_item in web_stream_iterator:
                    yield web_item
            elif item.endswith("answer"):  # 大模型回答
                item = next(stream_iterator)
                yield ServerSentEvent(event="answer",
                                      data=item[5:])
            else:  # 其他，忽略
                continue

    def web_stream(self, web_result: str):
        web_result_list = json.loads(
            json.loads(web_result[5:])["choices"][0]["delta"]["content"])
        for web_result in web_result_list:
            content = web_result["q"] + "\n" + web_result["sourceName"]
            time.sleep(random() * 0.5)
            yield ServerSentEvent(
                event="web",
                data={"id": "",
                      "object": "",
                      "created": 0,
                      "model": "",
                      "choices": [
                          {
                            "delta": {
                                "role": "assistant",
                                "content": content
                            },
                              "index": 0,
                              "finish_reason": "null"
                          }
                      ]})

    def parse_chat_request(self, chat_id, stream, content, detail):
        return {
            "chatId": chat_id,
            "stream": stream,
            "detail": detail,
            "messages": [{
                "content": content,
                "role": "user"
            }]
        }

    def dataset(self, request):
        request = self.parse_dataset_request(request)
        response = requests.post(url=self.dataset_url,
                                 json=request, headers=self.headers)
        return response

    def parse_dataset_request(self, raw_request):
        return {
            "pageNum": raw_request.page_num,
            "pageSize": raw_request.page_size,
            "collectionId": raw_request.collection_id,
            "searchText": raw_request.search_text
        }
