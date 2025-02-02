import os
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# Crear motor de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# Base declarativa de SQLAlchemy
Base = declarative_base()


# Modelo de Usuario
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    followers = Column(Integer, default=0)

    tweets = relationship("TweetDB", back_populates="user")


# Modelo de Tweets
class TweetDB(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    views = Column(Integer, default=0)
    link = Column(Text, nullable=False)
    profile_image = Column(Text)
    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )  # Fecha de creación del tweet
    received_at = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )  # Fecha cuando se guardó en la DB
    sent_by_user = Column(String(255), nullable=False)  # Quién mandó el tweet

    user = relationship("UserDB", back_populates="tweets")
