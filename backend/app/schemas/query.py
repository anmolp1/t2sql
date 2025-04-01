from typing import Optional, Dict, Any
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    database_connection_id: int
    use_case_id: Optional[int] = None

class SQLQueryResponse(BaseModel):
    sql_query: str
    explanation: str
    metadata: Optional[Dict[str, Any]] = None 