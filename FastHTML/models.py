# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column("user_id", Integer, primary_key=True)
    first_name = Column("first_name", String)
    last_name = Column("last_name", String)
    email = Column("email", String)
    picture = Column("picture", String)

    # Relationships
    trades = relationship("OptionTrade", back_populates="user")

class OptionTrade(Base):
    __tablename__ = 'option_trades'
    trade_id = Column("trade_id", Integer, primary_key=True)
    symbol = Column("symbol", String)
    option_type = Column("option_type", String)
    strike_price = Column("strike_price", Float)
    expiration_date = Column("expiration_date", DateTime)
    trade_date = Column("trade_date", DateTime)
    quantity = Column("quantity", Float)
    premium = Column("premium", Float)
    transaction_type = Column("transaction_type", String)
    
    # Relationships
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="trades")
