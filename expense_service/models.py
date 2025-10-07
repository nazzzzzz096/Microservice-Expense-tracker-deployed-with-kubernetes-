from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(100))
    amount = Column(DECIMAL(10,2), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())