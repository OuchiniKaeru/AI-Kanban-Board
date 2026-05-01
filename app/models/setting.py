from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value
        }
