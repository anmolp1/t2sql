from sqlalchemy import Column, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DatabaseMetadata(Base):
    __tablename__ = "database_metadata"

    id = Column(Integer, primary_key=True, index=True)
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"))
    datasets = Column(JSON, nullable=True)  # List of BigQuery datasets
    tables = Column(JSON, nullable=True)  # List of tables and their schemas
    relationships = Column(JSON, nullable=True)  # Table relationships
    constraints = Column(JSON, nullable=True)  # Database constraints
    
    database_connection = relationship("DatabaseConnection", back_populates="db_metadata_rel") 