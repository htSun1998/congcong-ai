from loguru import logger
from sse_starlette.sse import EventSourceResponse
from fastapi import HTTPException
from datetime import datetime
from lunardate import LunarDate
import json
import requests
from phone import Phone

from model.fastgpt import FastGPT
from model.kimi import KIMI
from model.whisper import Whisper
from model.censor import Censor
from model.coze import Coze
from model.web_searcher import WebSearcher
from common.message import DatasetRequest
from utils.constant import weekday_dict
from utils.encryption_util import EncryptionUtil


fastgpt = FastGPT()
kimi = KIMI()
whisper = Whisper()
censor = Censor()
coze = Coze()
encryption = EncryptionUtil()
web_searcher = WebSearcher()


def execute_chat(chat_id, stream, content, file, audio):
    logger.info(f"{chat_id}")

    ##### 内容审核 #####
    # 语音审核
    if audio is not None:
        if not censor.censor_audio(audio):
            logger.error("语音审核不通过")
            return HTTPException(status_code=400, detail="语音审核不通过")
        asr_result = whisper.asr(audio)
        if asr_result["status"] == 200:
            content = asr_result["response"]
            logger.info(f"语音输入：{content}")
        else:
            return HTTPException(status_code=500, detail="语音解析失败")
    # 文字审核
    else:
        censor_result = censor.censor_text(content)
        if censor_result["message"] != "合规":
            logger.error(f"文本审核不通过：{content}")
            content = censor.replace_keyword(censor_result, content)
            return HTTPException(status_code=400, detail=content)
        logger.info(f"文本输入：{content}")
    ##### 生成回复 #####
    # 若未上传文件，直接获取调用fastgpt进行知识库问答
    if file is None:
        if stream is True:
            response = fastgpt.chat_stream(chat_id, stream, content)
        else:
            response = fastgpt.chat(chat_id, stream, content)
    # 若上传文件，对接kimi大模型
    else:
        file = kimi.upload_file(file)
        if file is None:
            return HTTPException(status_code=500, detail="文件内容无法解析")
        file_id = file["file_id"]
        if stream is True:
            response = kimi.chat_stream(stream, content, file_id)
        else:
            response = kimi.chat(stream, content, file_id)

    ##### 消息输出 #####
    if stream is True:
        return EventSourceResponse(response)
    else:
        return response.json()


def execute_dataset(request: DatasetRequest):
    if request.type == "add":
        return fastgpt.add_data(request.data)
    elif request.type == "delete":
        return fastgpt.delete_data(request.data)
    elif request.type == "update":
        return fastgpt.update_data(request.data)
    else:
        return HTTPException(status_code=501, detail="未定义操作")
    # response = fastgpt.dataset(request)
    # data_list = []
    # for data in response.json()["data"]["data"]:
    #     data_list.append(data["q"])
    # return data_list


def execute_web(query):
    # return coze.web_search(query)
    return web_searcher.search(query)


def execute_time():
    now = datetime.now()
    weekday = now.strftime('%A')
    weekday_cn = weekday_dict[weekday]
    lunar_date = LunarDate.fromSolarDate(now.year, now.month, now.day)
    lunar_date_str = f"{lunar_date.year}年{lunar_date.month}月{lunar_date.day}日"
    result = (
        f"当前日期和时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"星期几: {weekday_cn}\n"
        f"农历日期: {lunar_date_str}\n"
    )

    return [{
        "id": "",
        "datasetId": "",
        "collectionId": "",
        "sourceName": "",
        "q": "今天日期信息",
        "a": result
    }]


def execute_weather(city, phone):
    if city == "":
        city = Phone().find(phone)['city']
    url = 'http://t.weather.sojson.com/api/weather/city/'
    with open("/data/projects/congcong-ai/assets/city.json", "r") as f:
        city_dict: dict = json.load(f)
        city = city_dict.get(city, None)
        if city is None:
            return []
        r = requests.get(url + city).json()
        result = (
            f"城市：{r['cityInfo']['parent']}, {r['cityInfo']['city']}\n"
            f"时间：{r['time']}, {r['data']['forecast'][0]['week']}\n"
            f"温度：{r['data']['forecast'][0]['high']}, {r['data']['forecast'][0]['low']}\n"
            f"天气：{r['data']['forecast'][0]['type']}"
        )
        return [{
            "id": "",
            "datasetId": "",
            "collectionId": "",
            "sourceName": "",
            "q": "天气信息",
            "a": result
        }]


def execute_equity(phone):
    # url = "https://hbgw.js118114.com/applet-web/equity/myEquity/initInfo"
    url = "https://testhbsh.js118114.com:8443/applet-web-test/equity/myEquity/initInfo"
    phone_encrypt = encryption.encrypt(phone)
    params = {"phone": phone_encrypt}
    res = requests.get(url=url, params=params).json()
    if res['data']:
        return [{
            "id": "",
            "datasetId": "",
            "collectionId": "",
            "sourceName": "",
            "q": r['memberName'],
            "a": f"可领取次数{r['count']}"
        } for r in res['data']]
    return []
