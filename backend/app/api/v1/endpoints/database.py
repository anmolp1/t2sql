from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.base_models import User
from app.schemas.database import (
    DatabaseConnection,
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    DatabaseMetadata,
    DatabaseMetadataCreate,
    DatabaseMetadataResponse
)
from app.services.database import (
    create_database_connection,
    get_database_connection,
    get_user_database_connections,
    update_database_connection,
    delete_database_connection,
    create_database_metadata,
    get_database_metadata,
    DatabaseService
)
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=DatabaseConnectionResponse)
def create_connection(
    connection: DatabaseConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new database connection."""
    logger.debug(f"Creating database connection for user {current_user.id}")
    db_connection = create_database_connection(db, connection, current_user.id)
    logger.debug(f"Created database connection with ID {db_connection.id}")
    return db_connection

@router.get("/", response_model=List[DatabaseConnectionResponse])
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all database connections for the current user."""
    logger.debug(f"Listing database connections for user {current_user.id}")
    connections = get_user_database_connections(db, current_user.id)
    logger.debug(f"Found {len(connections)} connections")
    return connections

@router.get("/{connection_id}", response_model=DatabaseConnectionResponse)
def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific database connection."""
    logger.debug(f"Getting database connection {connection_id} for user {current_user.id}")
    connection = get_database_connection(db, connection_id, current_user.id)
    if not connection:
        logger.warning(f"Database connection {connection_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Database connection not found")
    return connection

@router.put("/{connection_id}", response_model=DatabaseConnectionResponse)
def update_connection(
    connection_id: int,
    connection: DatabaseConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a database connection."""
    logger.debug(f"Updating database connection {connection_id} for user {current_user.id}")
    updated_connection = update_database_connection(db, connection_id, current_user.id, connection)
    if not updated_connection:
        logger.warning(f"Database connection {connection_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Database connection not found")
    return updated_connection

@router.delete("/{connection_id}")
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a database connection."""
    logger.debug(f"Deleting database connection {connection_id} for user {current_user.id}")
    success = delete_database_connection(db, connection_id, current_user.id)
    if not success:
        logger.warning(f"Database connection {connection_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Database connection not found")
    return {"message": "Database connection deleted successfully"}

@router.post("/{connection_id}/test")
def test_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test a database connection."""
    connection = get_database_connection(db, connection_id, current_user.id)
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    if DatabaseService.test_connection(connection):
        return {"status": "success", "message": "Connection successful"}
    else:
        raise HTTPException(status_code=400, detail="Connection failed")

@router.post("/{connection_id}/metadata", response_model=DatabaseMetadataResponse)
def extract_metadata(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract metadata from a database connection."""
    start_time = time.time()
    logger.info(f"Starting metadata extraction for connection {connection_id} for user {current_user.id}")
    
    try:
        # Check if metadata already exists
        logger.debug(f"Checking for existing metadata for connection {connection_id}")
        existing_metadata = get_database_metadata(db, connection_id)
        if existing_metadata:
            logger.info(f"Found existing metadata for connection {connection_id}, deleting it")
            db.delete(existing_metadata)
            db.commit()
            logger.debug("Existing metadata deleted successfully")
        
        # Get database connection
        logger.debug(f"Fetching database connection {connection_id}")
        connection = get_database_connection(db, connection_id, current_user.id)
        if not connection:
            logger.warning(f"Database connection {connection_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Database connection not found")
        logger.debug(f"Found database connection {connection_id}")
        
        # Extract metadata from BigQuery
        logger.info(f"Starting BigQuery metadata extraction for connection {connection_id}")
        bigquery_start = time.time()
        try:
            metadata_dict = DatabaseService.get_database_metadata(connection)
            bigquery_duration = time.time() - bigquery_start
            logger.info(f"BigQuery metadata extraction completed in {bigquery_duration:.2f} seconds")
        except Exception as e:
            logger.error(f"BigQuery metadata extraction failed after {time.time() - bigquery_start:.2f} seconds: {str(e)}", exc_info=True)
            raise
        
        # Create metadata record
        logger.debug(f"Creating metadata record for connection {connection_id}")
        db_start = time.time()
        try:
            metadata = create_database_metadata(
                db,
                DatabaseMetadataCreate(
                    database_connection_id=connection_id,
                    datasets=metadata_dict.get('datasets'),
                    tables=metadata_dict.get('tables'),
                    relationships=metadata_dict.get('relationships'),
                    constraints=metadata_dict.get('constraints')
                )
            )
            db_duration = time.time() - db_start
            logger.info(f"Database metadata creation completed in {db_duration:.2f} seconds")
        except Exception as e:
            logger.error(f"Database metadata creation failed after {time.time() - db_start:.2f} seconds: {str(e)}", exc_info=True)
            raise
        
        # Convert to response model
        logger.debug("Converting to response model")
        response = DatabaseMetadataResponse(
            id=metadata.id,
            database_connection_id=metadata.database_connection_id,
            datasets=metadata.datasets,
            tables=metadata.tables,
            relationships=metadata.relationships,
            constraints=metadata.constraints
        )
        
        total_duration = time.time() - start_time
        logger.info(f"Metadata extraction completed successfully in {total_duration:.2f} seconds")
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error for connection {connection_id}: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error extracting metadata for connection {connection_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error extracting metadata: {str(e)}")

@router.get("/{connection_id}/metadata", response_model=DatabaseMetadataResponse)
def get_connection_metadata(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get metadata for a database connection."""
    logger.debug(f"Getting metadata for database connection {connection_id} for user {current_user.id}")
    connection = get_database_connection(db, connection_id, current_user.id)
    if not connection:
        logger.warning(f"Database connection {connection_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    metadata = get_database_metadata(db, connection_id)
    if not metadata:
        logger.debug(f"Metadata not found for database connection {connection_id}, creating new metadata")
        # If metadata doesn't exist, create it
        metadata_dict = DatabaseService.get_database_metadata(connection)
        metadata = create_database_metadata(
            db,
            DatabaseMetadataCreate(
                database_connection_id=connection_id,
                datasets=metadata_dict.get('datasets'),
                tables=metadata_dict.get('tables'),
                relationships=metadata_dict.get('relationships'),
                constraints=metadata_dict.get('constraints')
            )
        )
    
    # Convert to response model
    return DatabaseMetadataResponse(
        id=metadata.id,
        database_connection_id=metadata.database_connection_id,
        datasets=metadata.datasets,
        tables=metadata.tables,
        relationships=metadata.relationships,
        constraints=metadata.constraints
    ) 