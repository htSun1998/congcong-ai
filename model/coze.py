import requests
from uuid import uuid1
import json
from loguru import logger
import yaml


class Coze:
    def __init__(self) -> None:
        with open('/data/projects/congcong-ai/config/config.yaml', 'r', encoding='utf-8') as f:
            args = yaml.load(f.read(), Loader=yaml.FullLoader)["coze"]
        self.url = args['url']
        self.api_key = "Bearer " + args['api_key']
        self.bot_id = args['bot_id']

    def web_search(self, query):
        data = {
            "bot_id": self.bot_id,
            "user_id": str(uuid1()),
            "auto_save_history": True,
            "additional_messages": [{
                "role": "user",
                "content": f"{query}",
                "content_type": "text"}],
            "stream": False
        }
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(
            url=self.url, json=data, headers=headers).json()
        response = self.parse_response(response, query)
        logger.debug(f"coze网络搜索结果：{response}")
        return response

    def parse_response(self, raw_response, query):
        logger.error(raw_response)
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
