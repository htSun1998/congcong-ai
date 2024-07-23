import requests
from sse_starlette import ServerSentEvent
import json
from random import random
import time
import yaml
from loguru import logger

from common.message import Data, Response


class FastGPT:
    def __init__(self) -> None:
        with open('/data/projects/congcong-ai/config/config.yaml', 'r', encoding='utf-8') as f:
            args = yaml.load(f.read(), Loader=yaml.FullLoader)["fastgpt"]
        self.chat_url = args['chat_url']
        self.dataset_add_url = args['dataset']['add_url']
        self.dataset_delete_url = args['dataset']['delete_url']
        self.dataset_update_url = args['dataset']['update_url']
        self.dataset_list_url = args['dataset']['list_url']
        self.dataset_id = args['dataset']['id']
        self.headers = {"Authorization": "Bearer " + args['api_key']}

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
        # for i in stream_iterator:
        #     logger.debug(i)
        while True:
            item: str | None = next(stream_iterator, None)
            if item is None:  # 结束
                break
            if item == "":  # 空行
                continue
            if item.endswith("fastAnswer"):  # 直接回答
                item = next(stream_iterator)
                fast_answer_stream_iterator = self.fast_answer_stream(item)
                for fast_answer_item in fast_answer_stream_iterator:
                    yield fast_answer_item
                # yield ServerSentEvent(event="fastAnswer",
                #                       data=item[5:])
            elif item.endswith("answer"):  # 大模型回答
                item = next(stream_iterator)
                yield ServerSentEvent(event="answer",
                                      data=item[5:])
            else:  # 其他，忽略
                continue

    def fast_answer_stream(self, fast_answer_result: str):
        try:
            fast_answer_result: list[dict] = json.loads(
                json.loads(fast_answer_result[5:])["choices"][0]["delta"]["content"])
            print(fast_answer_result)
            if "chunkIndex" in fast_answer_result[0].keys():  # 卡片展示分支
                yield ServerSentEvent(  # 直接返回第一条
                    event="card",
                    data={
                        "id": "",
                        "object": "",
                        "created": 0,
                        "model": "",
                        "choices": [
                            {
                                "delta": {
                                    "role": "assistant",
                                    "content": str(fast_answer_result[0])
                                },
                                "index": 0,
                                "finish_reason": "null"
                            }
                        ]})
            else:  # 网络搜索分支
                for web_result in fast_answer_result:
                    if web_result['sourceName'][5:] == "":  # 排除链接为空的情况
                        continue
                    content = web_result["a"] + "\n" + \
                        f"[复制链接]({web_result['sourceName'][5:]})"
                    time.sleep(random())  # 休眠0-1秒
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
        except:
            pass

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

    # def dataset(self, request):
    #     request = self.parse_dataset_request(request)
    #     response = requests.post(url=self.dataset_url,
    #                              json=request, headers=self.headers)
    #     return response

    # def parse_dataset_request(self, raw_request):
    #     return {
    #         "pageNum": raw_request.page_num,
    #         "pageSize": raw_request.page_size,
    #         "collectionId": raw_request.collection_id,
    #         "searchText": raw_request.search_text
    #     }

    def get_all_data(self) -> list:
        all_data = []
        res = ["init"]
        i = 0
        while res:
            i += 1
            body = {
                "pageNum": i,
                "pageSize": 30,
                "collectionId": self.dataset_id,
                "searchText": ""
            }
            res = requests.post(url=self.dataset_list_url,
                                headers=self.headers,
                                json=body).json()["data"]["data"]
            all_data += res
        return all_data

    def check_exist(self, raw_d: Data, all_data) -> str | None:
        """检查是否存在，不存在返回空字符串，存在返回raw_d的id 和 知识库知识id"""
        for d in all_data:
            if eval(d['a'])['id'] == raw_d.id:
                return raw_d.id, d['_id']  # 小程序知识id、知识库知识id
        return None, None

    def add_data(self, raw_data: list[Data]):
        """批量新增"""
        all_data = self.get_all_data()
        data = []
        error_data = []  # 需要增加但已存在的id
        for raw_d in raw_data:
            exist_id, _ = self.check_exist(raw_d, all_data)
            if exist_id is not None:
                error_data.append(exist_id)
                continue
            a = {
                "id": raw_d.id,  # 唯一id
                "pic": raw_d.pic,
                "path": raw_d.path,
                "title": raw_d.title,
                "location": raw_d.location
            }
            data.append({
                "q": raw_d.title,
                "a": str(a),
                "indexes": [{"text": index} for index in raw_d.keyword.split(",")] if raw_d.keyword != "" else []
            })
        body = {
            "collectionId": self.dataset_id,
            "trainingMode": "chunk",
            "data": data
        }
        # 判断是否有重复
        if error_data:
            return Response(code="0001", result="下列id内容重复" + str(error_data))
        res = requests.post(url=self.dataset_add_url,
                            headers=self.headers,
                            json=body).json()
        if res['code'] == 200:
            return Response(code="0000", result="全部新增成功")
        return Response(code="0001", result="新增失败")

    def delete_data(self, raw_data: list[Data]):
        """批量删除"""
        all_data = self.get_all_data()
        error_data = []  # 需要删除但不存在的id
        for raw_d in raw_data:
            exist_id, _ = self.check_exist(raw_d, all_data)
            if exist_id is None:
                error_data.append(raw_d.id)
        if error_data:
            return Response(code="0002", result="下列id内容不存在" + str(error_data))
        for raw_d in raw_data:
            _, _id = self.check_exist(raw_d, all_data)
            res = requests.delete(url=self.dataset_delete_url,
                                  headers=self.headers,
                                  params={'id': _id}).json()
            if res['code'] != 200:
                error_data.append(raw_d.id)
        if error_data:
            return Response(code="0002", result="部分删除失败" + str(error_data))
        return Response(code="0000", result="全部删除成功")

    def update_data(self, raw_data: list[Data]):
        """先删除、再添加"""
        # 删除
        res = self.delete_data(raw_data)
        if res.code == "0002":  # 删除失败
            return Response(code="0003", result="部分更新失败：" + res.result)
        res = self.add_data(raw_data)
        if res.code == "0001":  # 新增失败
            return Response(code="0003", result="部分新增失败：" + res.result)
        return Response(code="0000", result="更新成功")
