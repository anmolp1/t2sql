from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    connection_type = Column(String, nullable=False)
    host = Column(String, nullable=True)
    port = Column(String, nullable=True)
    database_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    dataset = Column(String, nullable=True)  # Added dataset field for BigQuery
    credentials_json = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    db_metadata = Column(JSON, nullable=True)  # Store database metadata directly
    
    user = relationship("User", back_populates="database_connections")
    db_metadata_rel = relationship("DatabaseMetadata", back_populates="database_connection", uselist=False)
    use_cases = relationship("UseCase", back_populates="database_connection")

class DatabaseMetadata(Base):
    __tablename__ = "database_metadata"

    id = Column(Integer, primary_key=True, index=True)
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"))
    datasets = Column(JSON, nullable=True)
    tables = Column(JSON, nullable=True)
    relationships = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)

    database_connection = relationship("DatabaseConnection", back_populates="db_metadata_rel")

class UseCase(Base):
    __tablename__ = "use_cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    example_query = Column(String, nullable=False)
    natural_language_example = Column(String, nullable=False)
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    database_connection = relationship("DatabaseConnection", back_populates="use_cases") 