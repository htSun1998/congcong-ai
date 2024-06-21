import requests
from uuid import uuid1
import json
from loguru import logger


class Coze:
    def __init__(self) -> None:
        self.url = "https://api.coze.cn/open_api/v2/chat"
        self.api_key = "Bearer " + \
            "pat_Jtwl4eB0WW3fCEkzw3Mlr3BPunm3Xfb0AxPVdXOyfWnL46KC81xaqPriYFxM0T1y"
        self.bot_id = "7368304530351505446"

    def web_search(self, query):
        data = {
            "conversation_id": str(uuid1()),
            "bot_id": self.bot_id,
            "user": str(uuid1()),
            "query": query,
            "stream": False
        }
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.cn",
            "Connection": "keep-alive"
        }
        response = requests.post(
            url=self.url, json=data, headers=headers).json()
        response = self.parse_response(response, query)
        logger.debug(f"coze网络搜索结果：{response}")
        return response

    def parse_response(self, raw_response, query):
        data_list = []
        try:  # 互联网搜索成功调用
            res_json = json.loads(raw_response["messages"][2]["content"])
            for res in res_json:
                res = res.split("\n")
                data = {
                    "id": "",
                    "datasetId": "",
                    "collectionId": "",
                    "sourceName": res[2],
                    "q": res[0],
                    "a": res[1]
                }
                data_list.append(data)
            return data_list
        except:  # 大模型直接回答
            return [{
                "id": "",
                "datasetId": "",
                "collectionId": "",
                "sourceName": "",
                "q": query,
                "a": raw_response["messages"][0]["content"]
            }]
