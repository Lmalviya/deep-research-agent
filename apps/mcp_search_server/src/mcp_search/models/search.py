from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    title: str = Field(
        description="Title of the search result",
    )

    url: HttpUrl = Field(
        description="URL of the search result",
    )

    snippet: str = Field(
        description="Short description/snippet of the result",
    )

    source_engine: str | None = Field(
        default=None,
        description="Search engine that produced the result",
    )


class SearchResponse(BaseModel):
    query: str = Field(
        description="Original search query",
    )

    results: list[SearchResult] = Field(
        default_factory=list,
        description="List of search results",
    )