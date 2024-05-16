from pydantic import BaseModel


class DatasetRequest(BaseModel):
    page_num: int
    page_size: int
    collection_id: str
    search_text: str = ""
