from typing import Optional
from fastapi import Body, FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




app=FastAPI()

class Post(BaseModel):
  title: str
  content: str
  published: bool = True
  
#database connection
# while True:
#   try:
#     conn = psycopg2.connect(host='localhost', database="fastapidb", user="postgres", password="admin", cursor_factory=RealDictCursor)
#     cursor = conn.cursor()
#     print("database connected succesfully!")
#     break
#   except Exception as error:
#     print("connection failed with database")
#     print("error", error)
#     time.sleep(3)


#root
@app.get("/")
def root():
  return {"data": "welcome to api"}

### with ORM sqlalchemy

#get posts
@app.get("/posts")
def test_db(db: Session = Depends(get_db)):
  posts = db.query(models.Post).all()
  return {"message": posts}


#create_post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def craete_post(post: Post, db: Session = Depends(get_db)):
  new_post = models.Post(**post.dict())
  db.add(new_post)
  db.commit()
  db.refresh(new_post)
  return {"message": f"Post Created!"}


#get post by id
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
  posts = db.query(models.Post).filter(models.Post.id == id).first()
  if not posts:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found!")
    # response.status_code = status.HTTP_404_NOT_FOUND
  return {"posts": posts}


# delete
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def post_delete(id: int, db: Session = Depends(get_db)):
  post = db.query(models.Post).filter(models.Post.id == id)
  if post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with {id} not found!")
  post.delete(synchronize_session=False)
  db.commit()

  return Response(status_code=status.HTTP_204_NO_CONTENT)


#update 
@app.put("/posts/{id}")
def post_update(id: int, updated_post: Post, db: Session = Depends(get_db)):
  post_query = db.query(models.Post).filter(models.Post.id == id)
  post = post_query.first()
  if post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with {id} not found!")
  post_query.update(updated_post.dict(), synchronize_session=False)
  db.commit()
  
  return {"message": post_query.first()}






## With SQL quer

#get all posts
# @app.get("/posts")
# def posts():
#   cursor.execute("""Select * from posts""")
#   posts = cursor.fetchall()
#   print(posts)
#   return {"posts": posts}

#create_post
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def craete_post(post: Post):
#   cursor.execute("""Insert into posts (title, content, published) values (%s, %s, %s) returning *""", (post.title, post.content, post.published))
#   new_post = cursor.fetchone()
#   conn.commit()
#   return {"message": new_post}
  

#get post based on id
# @app.get('/posts/{id}')
# def get_post(id: int):
#   cursor.execute("""Select * from posts where id =  %s""", (str(id),))
#   post = cursor.fetchone()
#   if not post:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found!")
#     # response.status_code = status.HTTP_404_NOT_FOUND
#   return {"posts": post}


#delete
# @app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
# def post_delete(id):
#   cursor.execute("""DELETE From posts where id = %s returning *""", (str(id),))
#   post = cursor.fetchone()
#   if post == None:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found!")
#   return Response(status_code=status.HTTP_204_NO_CONTENT)


#update
# @app.put("/posts/{id}")
# def post_update(id: int, post: Post):
#   cursor.execute("""update posts set title = %s, content= %s, published= %s where id = %s returning *""",
#                  (post.title, post.content, post.published, (str(id))))
#   post = cursor.fetchone()
#   conn.commit()
#   if post == None:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found!")
#   return {"message": post}





