from datetime import UTC, datetime

import pytest
from pydantic import BaseModel, ValidationError

from castoria.common.clients.models.http_response import HTTPResponse, HTTPResponseMetadata


class SampleData(BaseModel):
    id: int
    name: str


@pytest.fixture
def metadata() -> HTTPResponseMetadata:
    return HTTPResponseMetadata(
        timestamp=datetime.now(UTC),
        status="OK",
        status_code=200,
        elapsed_ms=100,
    )


def test_http_response_metadata(metadata: HTTPResponseMetadata) -> None:
    assert metadata.status_code == 200
    assert metadata.error_message is None


def test_http_response_generic(metadata: HTTPResponseMetadata) -> None:
    response = HTTPResponse[list[SampleData]](
        metadata=metadata,
        data=[{"id": 1, "name": "Artoria"}],
    )

    assert response.data is not None
    assert isinstance(response.data[0], SampleData)
    assert response.data[0].name == "Artoria"


def test_http_response_invalid_status_code() -> None:
    with pytest.raises(ValidationError):
        HTTPResponseMetadata(
            timestamp=datetime.now(UTC),
            status="Invalid",
            status_code=999,
            elapsed_ms=100,
        )
