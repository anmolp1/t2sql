from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class DatabaseConnectionBase(BaseModel):
    name: str
    connection_type: str
    host: Optional[str] = None
    port: Optional[str] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    project_id: Optional[str] = None
    dataset: Optional[str] = None
    credentials_json: Optional[Dict[str, Any]] = None

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass

class DatabaseConnectionUpdate(DatabaseConnectionBase):
    pass

class DatabaseConnectionInDB(DatabaseConnectionBase):
    id: int
    user_id: int
    db_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DatabaseConnection(DatabaseConnectionInDB):
    pass

class DatabaseConnectionResponse(DatabaseConnectionInDB):
    pass

class DatabaseMetadataBase(BaseModel):
    datasets: Optional[List[Dict[str, Any]]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[List[Dict[str, Any]]] = None

class DatabaseMetadataCreate(DatabaseMetadataBase):
    database_connection_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class DatabaseMetadataUpdate(DatabaseMetadataBase):
    pass

class DatabaseMetadataInDB(DatabaseMetadataBase):
    id: int
    database_connection_id: int

    class Config:
        from_attributes = True

class DatabaseMetadata(DatabaseMetadataInDB):
    pass

class DatabaseMetadataResponse(DatabaseMetadataInDB):
    pass 