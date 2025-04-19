from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship  
from sqlalchemy.sql import func  
import enum  
import uuid  

Base = declarative_base()  

class User(Base):  
    __tablename__ = "users"  
    
    id = Column(Integer, primary_key=True, index=True)  
    username = Column(String(50), unique=True, index=True, nullable=False)  
    email = Column(String(100), unique=True, index=True, nullable=False)  
    hashed_password = Column(String(255), nullable=False)  
    full_name = Column(String(100))  
    balance = Column(Float, default=0.0)  
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  
    is_active = Column(Boolean, default=True)  
    
    # 建立关系  
    transactions = relationship("Transaction", back_populates="user")  
    profile = relationship("UserProfile", back_populates="user", uselist=False)  
    conversations = relationship("Conversation", back_populates="user")  

class RiskProfile(str, enum.Enum):  
    CONSERVATIVE = "conservative"  
    BALANCED = "balanced"  
    AGGRESSIVE = "aggressive"  

class UserProfile(Base):  
    __tablename__ = "user_profiles"  
    
    id = Column(Integer, primary_key=True, index=True)  
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)  
    risk_profile = Column(Enum(RiskProfile), nullable=False)  
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  
    
    # 建立关系  
    user = relationship("User", back_populates="profile")  

class Product(Base):  
    __tablename__ = "products"  
    
    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String(100), nullable=False)  
    price_per_ounce = Column(Float, nullable=False)  
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  
    
    # 建立关系  
    transactions = relationship("Transaction", back_populates="product")  

class TransactionType(str, enum.Enum):  
    BUY = "buy"  
    SELL = "sell"  

class Transaction(Base):  
    __tablename__ = "transactions"  
    
    id = Column(Integer, primary_key=True, index=True)  
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  
    product_id = Column(Integer, ForeignKey("products.id"))  
    transaction_type = Column(Enum(TransactionType), nullable=False)  
    amount = Column(Float, nullable=False)  
    price_per_ounce = Column(Float, nullable=False)  
    total_price = Column(Float, nullable=False)  
    transaction_date = Column(DateTime, server_default=func.now())  
    
    # 建立关系  
    user = relationship("User", back_populates="transactions")  
    product = relationship("Product", back_populates="transactions")  

class CampaignStatus(str, enum.Enum):  
    NOT_STARTED = "NOT_STARTED"  
    IN_PROGRESS = "IN_PROGRESS"  
    EXPIRED = "EXPIRED"  

class MarketingCampaign(Base):  
    __tablename__ = "marketing_campaigns"  
    
    id = Column(Integer, primary_key=True, index=True)  
    title = Column(String(100), nullable=False)  
    description = Column(Text, nullable=False)  
    status = Column(Enum(CampaignStatus), nullable=False)  
    start_date = Column(DateTime, nullable=False)  
    end_date = Column(DateTime, nullable=False)  
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  

# 会话和消息模型  

class Conversation(Base):  
    __tablename__ = "conversations"  
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  
    title = Column(String(255), default="New Conversation")  
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  
    
    # 建立关系  
    user = relationship("User", back_populates="conversations")  
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")  

class Message(Base):  
    __tablename__ = "messages"  
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))  
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'  
    content = Column(Text, nullable=False)  
    created_at = Column(DateTime, server_default=func.now())  
    
    # 建立关系  
    conversation = relationship("Conversation", back_populates="messages")  