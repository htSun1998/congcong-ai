import uvicorn
from fastapi import Depends, FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as redis
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager

from common.message import DatasetRequest, WebRequest, WeatherRequest
from execute import execute_chat, execute_dataset, execute_web, execute_time, execute_weather, execute_equity


executor = ThreadPoolExecutor(max_workers=200)

@asynccontextmanager  # 启动时运行
async def lifespan(app: FastAPI):
    redis_connection = redis.from_url("redis://125.75.69.37:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.post("/congcong/chat", dependencies=[Depends(RateLimiter(times=200, seconds=1))])
def congcong_chat(chat_id: str = Form(...),
                  stream: bool = Form(True),
                  content: str = Form(None),
                  file: UploadFile = File(None),
                  audio: UploadFile = File(None)):
    """聊天接口"""
    future = executor.submit(execute_chat, chat_id, stream, content, file, audio)
    return future.result()


@app.post("/congcong/dataset")
def congcong_dataset(request: DatasetRequest):
    """数据集查询"""
    future = executor.submit(execute_dataset, request)
    return future.result()


@app.post("/congcong/web")
def congcong_web(request: WebRequest):
    """网络搜索"""
    future = executor.submit(execute_web, request.query)
    return future.result()


@app.get("/congcong/time")
def congcong_time():
    """时间查询"""
    future = executor.submit(execute_time)
    return future.result()


@app.post("/congcong/weather")
def congcong_weather(request: WeatherRequest):
    """天气查询"""
    future = executor.submit(execute_weather, request.city, request.phone)
    return future.result()


@app.get("/congcong/equity")
def congcong_weather(phone: str):
    """权益查询"""
    future = executor.submit(execute_equity, phone)
    return future.result()


if __name__ == "__main__":
    # 日志
    logger.add("logs/{time:YYYY-MM-DD}.log",
           rotation="1 day",
           retention="3 days",
           compression="zip")
    # 启动
    uvicorn.run(app='app:app',
                host="0.0.0.0",
                port=3200)
