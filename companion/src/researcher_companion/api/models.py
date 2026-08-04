from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.title() for part in tail)


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class SessionBootstrapRequest(ApiModel):
    office_host: Literal["Word"]
    office_platform: Literal["PC", "Mac"]
    word_api_13_supported: Literal[True]


class SessionBootstrapResponse(ApiModel):
    csrf_token: str
    expires_at: datetime


class ComponentHealth(ApiModel):
    database: Literal["ready"]
    content_store: Literal["ready"]
    worker: Literal["ready"]


class HealthResponse(ApiModel):
    schema_version: Literal[1] = 1
    status: Literal["ok"] = "ok"
    version: str
    components: ComponentHealth


class ErrorResponse(ApiModel):
    code: str
    message: str
