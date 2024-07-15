import requests
from uuid import uuid1
import itertools
import yaml

from utils.utils import convert_uploadfile_to_base64, find_values


class Censor:
    def __init__(self) -> None:
        with open('/data/projects/congcong-ai/config/config.yaml', 'r', encoding='utf-8') as f:
            args = yaml.load(f.read(), Loader=yaml.FullLoader)["censor"]
        self.text_censor_url = args['text_censor_url']
        self.audio_censor_url = args['audio_censor_url']
    
    def censor_text(self, content: str):
        request = self.parse_text_request(content)
        response = requests.post(url=self.text_censor_url, json=request)
        return response.json()
    
    def censor_audio(self, audio):
        if audio is None:
            return True
        audio_base64 = convert_uploadfile_to_base64(audio)
        request = self.parse_audio_request(audio_base64)
        response = requests.post(url=self.audio_censor_url, json=request)
        if response.json()["message"] != "合规":
            return False
        return True
    
    def parse_text_request(self, content: str):
        return {
            "uuid": str(uuid1()),
            "username": "congcong",
            "content": content
        }
    
    def parse_audio_request(self, audio_base64):
        return {
            "uuid": str(uuid1()),
            "username": "congcong",
            "base64": audio_base64
        }
    
    def replace_keyword(self, censor_result: dict, content: str):
        keywords, keywords_copy = itertools.tee(find_values(censor_result, "keyword"), 2)
        try:
            next(iter(keywords_copy))
        except:
            return "*" * len(content)
        for keyword in keywords:
            content = content.replace(keyword, "*" * len(keyword))
        return content
