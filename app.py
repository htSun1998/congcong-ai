import uvicorn
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from model.fastgpt import FastGPT
from model.kimi import KIMI
from model.whisper import Whisper
from model.censor import Censor
from common.message import DatasetRequest


app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

fastgpt = FastGPT()
kimi = KIMI()
whisper = Whisper()
censor = Censor()


@app.post("/congcong/chat")
async def congcong_chat(chat_id: str = Form(...),
                        stream: bool = Form(True),
                        content: str = Form(None),
                        file: UploadFile = File(None),
                        audio: UploadFile = File(None)):
    logger.info(f"{chat_id}")

    ##### 内容审核 #####
    # 语音审核
    if audio is not None:
        if not await censor.censor_audio(audio):
            return HTTPException(status_code=400, detail="语音审核不通过")
        asr_result = whisper.asr(audio)
        if asr_result["status"] == 200:
            content = asr_result["response"]
        else:
            return HTTPException(status_code=500, detail="语音解析失败")
    # 文字审核
    else:
        censor_result = censor.censor_text(content)
        if censor_result["message"] != "合规":
            content = censor.replace_keyword(censor_result, content)
            return HTTPException(status_code=400, detail=content)
    
    logger.info(f"{content}")
    ##### 生成回复 #####
    # 若未上传文件，直接获取调用fastgpt进行知识库问答
    if file is None:
        if stream is True:
            response = fastgpt.chat_stream(chat_id, stream, content)
        else:
            response = fastgpt.chat(chat_id, stream, content)
    # 若上传文件，对接kimi大模型
    else:
        file_id = kimi.upload_file(file)["file_id"]
        if stream is True:
            response = kimi.chat_stream(stream, content, file_id)
        else:
            response = kimi.chat(stream, content, file_id)

    ##### 消息输出 #####
    if stream is True:
        return EventSourceResponse(response)
    else:
        return response.json()


@app.post("/congcong/dataset")
async def congcong_dataset(request: DatasetRequest):
    response = fastgpt.dataset(request)
    data_list = []
    for data in response.json()["data"]["data"]:
        data_list.append(data["q"])
    return data_list


if __name__ == "__main__":
    # 日志
    logger.add("logs/{time:YYYY-MM-DD}.log",
           rotation="1 day",
           retention="3 days",
           compression="zip")
    # 启动
    uvicorn.run(app='app:app',
                host="0.0.0.0",
                port=3100,
                workers=1)
