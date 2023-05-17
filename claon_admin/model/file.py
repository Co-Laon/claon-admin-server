from pydantic import BaseModel


class UploadFileResponseDto(BaseModel):
    file_url: str
