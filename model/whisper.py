import requests
import yaml


class Whisper:
    def __init__(self) -> None:
        with open('/data/projects/congcong-ai/config/config.yaml', 'r', encoding='utf-8') as f:
            args = yaml.load(f.read(), Loader=yaml.FullLoader)["whisper"]
        self.url = args['url']

    def asr(self, audio):
        audio.file.seek(0)
        response = requests.post(url=self.url, files={"audio": (audio.filename, audio.file)})
        return response.json()
