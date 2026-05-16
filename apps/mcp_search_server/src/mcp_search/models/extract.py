from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl


class ExtractResponse(BaseModel):
    url: HttpUrl = Field(
        description="The extracted webpage URL",
    )

    title: str | None = Field(
        default=None,
        description="Extracted webpage title",
    )

    content: str = Field(
        description="Clean extracted markdown content",
    )

    raw_content_length: int | None = Field(
        default=None,
        description="Length of extracted content in characters",
    )