import base64
from fastapi import UploadFile


def convert_uploadfile_to_base64(file: UploadFile) -> str:
    # 读取文件的内容
    file.file.seek(0)
    file_content = file.file.read()
    # 编码为Base64字符串
    encoded_content = base64.b64encode(file_content)
    # 将bytes类型转为str，以得到Base64编码的字符串
    base64_string = encoded_content.decode('utf-8')
    return base64_string


def find_values(json_input, key):
    """
    查找并返回所有键名为key的值。
    :param json_input: 输入的JSON对象（字典或列表）
    :param key: 要查找的键名
    :return: 所有找到的值的列表
    """
    if isinstance(json_input, dict):
        for json_key, value in json_input.items():
            if json_key == key:
                yield value
            if isinstance(value, (dict, list)):
                yield from find_values(value, key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from find_values(item, key)
