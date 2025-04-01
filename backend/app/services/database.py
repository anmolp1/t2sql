from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from app.models.base_models import DatabaseConnection, DatabaseMetadata
from app.schemas.database import DatabaseConnectionCreate, DatabaseConnectionUpdate, DatabaseMetadataCreate
from app.core.config import settings

def create_database_connection(
    db: Session,
    connection: DatabaseConnectionCreate,
    user_id: int
) -> DatabaseConnection:
    """Create a new database connection."""
    db_connection = DatabaseConnection(
        **connection.dict(),
        user_id=user_id
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

def get_database_connection(
    db: Session,
    connection_id: int,
    user_id: int
) -> Optional[DatabaseConnection]:
    """Get a database connection by ID."""
    return db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.user_id == user_id
    ).first()

def get_user_database_connections(
    db: Session,
    user_id: int
) -> List[DatabaseConnection]:
    """Get all database connections for a user."""
    return db.query(DatabaseConnection).filter(
        DatabaseConnection.user_id == user_id
    ).all()

def update_database_connection(
    db: Session,
    connection_id: int,
    user_id: int,
    connection: DatabaseConnectionUpdate
) -> Optional[DatabaseConnection]:
    """Update a database connection."""
    db_connection = get_database_connection(db, connection_id, user_id)
    if not db_connection:
        return None
    
    for key, value in connection.dict(exclude_unset=True).items():
        setattr(db_connection, key, value)
    
    db.commit()
    db.refresh(db_connection)
    return db_connection

def delete_database_connection(
    db: Session,
    connection_id: int,
    user_id: int
) -> bool:
    """Delete a database connection."""
    db_connection = get_database_connection(db, connection_id, user_id)
    if not db_connection:
        return False
    
    db.delete(db_connection)
    db.commit()
    return True

def create_database_metadata(
    db: Session,
    metadata: DatabaseMetadataCreate
) -> DatabaseMetadata:
    """Create database metadata."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Create model instance with required fields
        db_metadata = DatabaseMetadata(
            database_connection_id=metadata.database_connection_id,
            datasets=metadata.datasets,
            tables=metadata.tables,
            relationships=metadata.relationships,
            constraints=metadata.constraints
        )
        logger.debug(f"Creating metadata for connection {metadata.database_connection_id}")
        db.add(db_metadata)
        db.commit()
        logger.debug(f"Successfully created metadata for connection {metadata.database_connection_id}")
        db.refresh(db_metadata)
        return db_metadata
    except Exception as e:
        logger.error(f"Error creating database metadata: {str(e)}")
        db.rollback()
        raise

def get_database_metadata(
    db: Session,
    connection_id: int
) -> Optional[DatabaseMetadata]:
    """Get metadata for a database connection."""
    return db.query(DatabaseMetadata).filter(
        DatabaseMetadata.database_connection_id == connection_id
    ).first()

class DatabaseService:
    @staticmethod
    def get_connection_url(connection: DatabaseConnection) -> str:
        """Get the connection URL for BigQuery."""
        return f"bigquery://{connection.project_id}"

    @staticmethod
    def create_engine(connection: DatabaseConnection):
        """Create a BigQuery engine using the connection details."""
        from google.cloud import bigquery
        from google.oauth2 import service_account
        import logging
        
        logger = logging.getLogger(__name__)
        try:
            if not connection.credentials_json:
                raise ValueError("No credentials provided")
            if not connection.project_id:
                raise ValueError("No project ID provided")
                
            credentials = service_account.Credentials.from_service_account_info(
                connection.credentials_json
            )
            client = bigquery.Client(credentials=credentials, project=connection.project_id)
            logger.debug(f"Successfully created BigQuery client for project {connection.project_id}")
            return client
        except Exception as e:
            logger.error(f"Error creating BigQuery client: {str(e)}")
            raise

    @staticmethod
    def get_database_metadata(connection: DatabaseConnection) -> Dict[str, Any]:
        """Get metadata for the BigQuery connection."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            metadata = DatabaseService._get_bigquery_metadata(connection)
            logger.debug(f"Successfully extracted metadata for connection {connection.id}")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata for connection {connection.id}: {str(e)}")
            raise

    @staticmethod
    def _get_bigquery_metadata(connection: DatabaseConnection) -> Dict[str, Any]:
        """Get BigQuery-specific metadata."""
        import logging
        import time
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating BigQuery client for project {connection.project_id}")
            client_start = time.time()
            try:
                client = DatabaseService.create_engine(connection)
                client_duration = time.time() - client_start
                logger.info(f"BigQuery client created in {client_duration:.2f} seconds")
            except Exception as e:
                logger.error(f"Failed to create BigQuery client after {time.time() - client_start:.2f} seconds: {str(e)}", exc_info=True)
                raise
            
            # Get datasets
            logger.info("Starting to fetch datasets")
            datasets_start = time.time()
            datasets = []
            dataset_count = 0
            table_count = 0
            
            try:
                for dataset in client.list_datasets():
                    dataset_count += 1
                    dataset_ref = dataset.reference
                    logger.debug(f"Processing dataset {dataset.dataset_id} ({dataset_count})")
                    tables = []
                    
                    # Get tables in dataset
                    try:
                        for table in client.list_tables(dataset_ref):
                            table_count += 1
                            table_ref = table.reference
                            logger.debug(f"Processing table {table.table_id} ({table_count})")
                            
                            try:
                                schema = client.get_table(table_ref).schema
                                logger.debug(f"Retrieved schema for table {table.table_id}")
                                
                                # Get columns
                                columns = []
                                for field in schema:
                                    columns.append({
                                        "name": field.name,
                                        "type": str(field.field_type),
                                        "mode": field.mode,
                                        "description": field.description
                                    })
                                
                                tables.append({
                                    "name": table.table_id,
                                    "columns": columns
                                })
                                logger.debug(f"Processed {len(columns)} columns for table {table.table_id}")
                            except Exception as e:
                                logger.error(f"Error processing table {table.table_id}: {str(e)}", exc_info=True)
                                continue
                    except Exception as e:
                        logger.error(f"Error listing tables for dataset {dataset.dataset_id}: {str(e)}", exc_info=True)
                        continue
                    
                    datasets.append({
                        "name": dataset.dataset_id,
                        "tables": tables
                    })
                    logger.debug(f"Completed processing dataset {dataset.dataset_id} with {len(tables)} tables")
            except Exception as e:
                logger.error(f"Error listing datasets: {str(e)}", exc_info=True)
                raise
            
            datasets_duration = time.time() - datasets_start
            logger.info(f"Fetched {dataset_count} datasets and {table_count} tables in {datasets_duration:.2f} seconds")
            
            metadata = {
                "datasets": datasets
            }
            return metadata
            
        except Exception as e:
            logger.error(f"Error in _get_bigquery_metadata: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def test_connection(connection: DatabaseConnection) -> bool:
        """Test if the BigQuery connection is valid."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            client = DatabaseService.create_engine(connection)
            # Try to list datasets to verify connection
            next(client.list_datasets())
            logger.debug(f"Successfully tested connection for project {connection.project_id}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False 