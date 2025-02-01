import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()


# Define the User model for the database
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    followers = Column(Integer, default=0)
    additional_info = Column(Text, nullable=True)

    # Relationship to tweets
    tweets = relationship("TweetDB", back_populates="user")


# Define the Tweet model for the database
class TweetDB(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(50), unique=True, nullable=False)
    text = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    views = Column(Integer, default=0)
    link = Column(Text, nullable=False)
    profile_image = Column(Text)
    created_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    sent_by_user = Column(String(255), nullable=True)

    # Foreign key to UserDB
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("UserDB", back_populates="tweets")


# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)


# Pydantic models for validation
class User(BaseModel):
    username: str
    followers: int = 0
    additional_info: str = None

    class Config:
        from_attributes = True


class Tweet(BaseModel):
    tweet_id: str
    text: str
    likes: int = 0
    retweets: int = 0
    views: int = 0
    link: str
    profile_image: str = None
    created_at: datetime
    sent_by_user: str
    user: User

    class Config:
        from_attributes = True


# Initialize FastAPI
app = FastAPI()


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tweets", status_code=201)
def create_tweets(tweets: List[Tweet], db: Session = Depends(get_db)):
    """
    Endpoint to receive and store a batch of tweets.
    """
    try:
        for tweet in tweets:
            # Verificar si el tweet ya existe en la base de datos
            existing_tweet = (
                db.query(TweetDB).filter(TweetDB.tweet_id == tweet.tweet_id).first()
            )
            if existing_tweet:
                print(f"⚠️ Tweet with ID {tweet.tweet_id} already exists. Skipping.")
                continue  # Omitir tweets duplicados

            # Verificar si el usuario existe o crearlo
            user = (
                db.query(UserDB).filter(UserDB.username == tweet.user.username).first()
            )
            if not user:
                user = UserDB(
                    username=tweet.user.username,
                    followers=tweet.user.followers,
                    additional_info=tweet.user.additional_info,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Crear y agregar el nuevo tweet
            new_tweet = TweetDB(
                tweet_id=tweet.tweet_id,
                text=tweet.text,
                likes=tweet.likes,
                retweets=tweet.retweets,
                views=tweet.views,
                link=tweet.link,
                profile_image=tweet.profile_image,
                created_at=tweet.created_at,
                sent_by_user=tweet.sent_by_user,
                user_id=user.id,
            )
            db.add(new_tweet)

        db.commit()
        return {"message": "Tweets stored successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
