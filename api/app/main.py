import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .models import (
    Base,
    UserDB,
    TweetDB,
    engine,
    SessionLocal,
)

# Cargar variables de entorno
load_dotenv()

# Configurar cache en memoria
tweet_ids_cache = set()

# Lifespan para manejar eventos de inicio y cierre de la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    global tweet_ids_cache
    with SessionLocal() as db:
        tweet_ids_cache = {row[0] for row in db.query(TweetDB.tweet_id).all()}
        print(f"🚀 Cache inicializado con {len(tweet_ids_cache)} tweets.")
    yield
    tweet_ids_cache.clear()
    print("🧹 Cache limpiado.")

# Crear la app con lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/", tags=["Health Check"])
async def health_check():
    return JSONResponse(content={"status": "ok", "message": "Service is running"})

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic
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
    replies: int = 0
    bookmarks: int = 0
    link: str
    profile_image: str = None
    created_at: datetime
    sent_by_user: str
    user: User

    class Config:
        from_attributes = True

# Endpoint para recibir tweets
@app.post("/tweets", status_code=201)
def create_tweets(tweets: List[Tweet], db: Session = Depends(get_db)):
    try:
        new_tweets = []
        for tweet in tweets:
            # Verificar si el tweet ya está en el cache
            if tweet.tweet_id in tweet_ids_cache:
                continue  # Omitir tweets duplicados

            # Verificar si el usuario existe o crearlo
            user = (
                db.query(UserDB).filter(UserDB.username == tweet.user.username).first()
            )
            if not user:
                user = UserDB(
                    username=tweet.user.username, followers=tweet.user.followers
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
                replies=tweet.replies,  # Nuevo campo
                bookmarks=tweet.bookmarks,  # Nuevo campo
                link=tweet.link,
                profile_image=tweet.profile_image,
                created_at=tweet.created_at,
                sent_by_user=tweet.sent_by_user,
                user_id=user.id,
            )
            new_tweets.append(new_tweet)
            tweet_ids_cache.add(tweet.tweet_id)  # Actualizar cache

        db.add_all(new_tweets)
        db.commit()
        return {"message": f"{len(new_tweets)} Tweets almacenados con éxito."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
