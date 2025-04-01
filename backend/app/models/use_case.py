from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UseCase(Base):
    __tablename__ = "use_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    example_query = Column(Text)
    natural_language_example = Column(Text)
    
    # Foreign key to database connection
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"))
    database_connection = relationship("DatabaseConnection", back_populates="use_cases") 