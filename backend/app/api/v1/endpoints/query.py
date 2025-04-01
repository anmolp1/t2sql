from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.database_connection import DatabaseConnection
from app.models.database_metadata import DatabaseMetadata
from app.models.use_case import UseCase
from app.services.sql_generation import SQLGenerationService
from app.schemas.query import QuestionRequest, SQLQueryResponse

router = APIRouter()

@router.post("/{connection_id}/generate", response_model=SQLQueryResponse)
async def generate_sql_query(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
    question_in: QuestionRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate SQL query from natural language question.
    """
    # Get database connection
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.user_id == current_user.id
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    # Get database metadata
    metadata = db.query(DatabaseMetadata).filter(
        DatabaseMetadata.database_connection_id == connection_id
    ).first()
    if not metadata:
        raise HTTPException(status_code=404, detail="Database metadata not found")
    
    # Get use cases for this database
    use_cases = db.query(UseCase).filter(
        UseCase.database_connection_id == connection_id
    ).all()
    use_cases_dict = [
        {
            "natural_language_example": case.natural_language_example,
            "example_query": case.example_query
        }
        for case in use_cases
    ] if use_cases else None
    
    # Generate SQL query
    sql_service = SQLGenerationService()
    try:
        result = await sql_service.generate_sql(
            question_in.question,
            metadata,
            connection,
            use_cases_dict
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL query: {str(e)}"
        ) 