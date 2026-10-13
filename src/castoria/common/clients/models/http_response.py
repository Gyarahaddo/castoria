from datetime import datetime

from pydantic import BaseModel, Field


class HTTPResponseMetadata(BaseModel):
    timestamp: datetime
    status: str
    status_code: int = Field(ge=100, le=599)
    error_message: str | None = None
    elapsed_ms: int = Field(ge=0)


class HTTPResponse[T](BaseModel):
    metadata: HTTPResponseMetadata
    data: T | None = None
