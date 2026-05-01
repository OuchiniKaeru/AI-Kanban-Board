from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class KanbanColumn(Base):
    __tablename__ = "columns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="columns")
    tasks = relationship("Task", back_populates="column", lazy="selectin")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "order_index": self.order_index,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
