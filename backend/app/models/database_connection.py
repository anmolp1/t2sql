from sqlalchemy import Column, Integer, String, JSON, ForeignKey
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