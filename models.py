from pydantic import BaseModel


class Book(BaseModel):
    author: str | None = None
    name: str
    link: str
    price: float
    store: str
    image_url: str
