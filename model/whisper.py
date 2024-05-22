import requests


class Whisper:
    def __init__(self) -> None:
        self.url = "http://125.75.69.37:8504/audio"

    def asr(self, audio):
        audio.file.seek(0)
        response = requests.post(url=self.url, files={"audio": (audio.filename, audio.file)})
        return response.json()
