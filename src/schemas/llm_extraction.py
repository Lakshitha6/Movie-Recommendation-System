from pydantic import BaseModel

class QueryExtract(BaseModel):

    """
    Helper schema for get llm output according to specific structure.
    
    """

    actor: str | None = None
    director: str | None = None
    genre: str | None = None
    semantic_query: str | None = None