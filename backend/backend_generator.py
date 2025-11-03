# Full-Stack Backend Generator - SUPERIOR to Emergent
from typing import Dict, List
import re

class BackendGenerator:
    """Generate complete FastAPI backend with database, auth, and APIs"""
    
    def __init__(self):
        self.models = []
        self.endpoints = []
    
    async def generate_fullstack_app(self, user_prompt: str) -> Dict[str, str]:
        """Generate complete full-stack application with backend"""
        
        files = {}
        
        # Analyze what kind of app is needed
        app_type = self._analyze_app_type(user_prompt)
        
        # Generate backend files
        files['backend/main.py'] = self._generate_fastapi_main(user_prompt, app_type)
        files['backend/models.py'] = self._generate_database_models(user_prompt, app_type)
        files['backend/auth.py'] = self._generate_auth_system()
        files['backend/database.py'] = self._generate_database_config()
        files['backend/requirements.txt'] = self._generate_requirements()
        files['backend/.env'] = self._generate_env_file()
        
        # Generate frontend files
        files['frontend/index.html'] = self._generate_frontend_html(user_prompt, app_type)
        files['frontend/app.js'] = self._generate_frontend_js(app_type)
        files['frontend/style.css'] = self._generate_frontend_css()
        
        # Generate docker and deployment files
        files['Dockerfile'] = self._generate_dockerfile()
        files['docker-compose.yml'] = self._generate_docker_compose()
        files['README.md'] = self._generate_fullstack_readme(user_prompt)
        files['.gitignore'] = self._generate_gitignore()
        
        return files
    
    def _analyze_app_type(self, prompt: str) -> str:
        """Analyze what type of application to build"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['social', 'twitter', 'facebook', 'post', 'feed']):
            return 'social'
        elif any(word in prompt_lower for word in ['ecommerce', 'store', 'shop', 'product', 'cart']):
            return 'ecommerce'
        elif any(word in prompt_lower for word in ['blog', 'article', 'cms', 'content']):
            return 'blog'
        elif any(word in prompt_lower for word in ['todo', 'task', 'project management', 'kanban']):
            return 'todo'
        elif any(word in prompt_lower for word in ['chat', 'messaging', 'message']):
            return 'chat'
        else:
            return 'crud'
    
    def _generate_fastapi_main(self, prompt: str, app_type: str) -> str:
        """Generate FastAPI main.py with all endpoints"""
        
        if app_type == 'social':
            return '''from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, auth, database
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Social Media App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PostCreate(BaseModel):
    content: str
    image_url: str = None

class CommentCreate(BaseModel):
    post_id: int
    content: str

# Auth Endpoints
@app.post("/api/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = auth.create_access_token(db_user.id)
    return {"access_token": token, "user": {"id": db_user.id, "username": db_user.username}}

@app.post("/api/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth.create_access_token(user.id)
    return {"access_token": token, "user": {"id": user.id, "username": user.username}}

@app.get("/api/auth/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}

# Post Endpoints
@app.post("/api/posts")
def create_post(post: PostCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_post = models.Post(
        content=post.content,
        image_url=post.image_url,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/api/posts")
def get_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

# Like Endpoints
@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Check if already liked
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"liked": False}
    else:
        like = models.Like(post_id=post_id, user_id=current_user.id)
        db.add(like)
        db.commit()
        return {"liked": True}

# Comment Endpoints
@app.post("/api/comments")
def create_comment(comment: CommentCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_comment = models.Comment(
        post_id=comment.post_id,
        user_id=current_user.id,
        content=comment.content,
        created_at=datetime.utcnow()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/api/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
    return comments

# Follow Endpoints
@app.post("/api/users/{user_id}/follow")
def follow_user(user_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()
    
    if existing_follow:
        db.delete(existing_follow)
        db.commit()
        return {"following": False}
    else:
        follow = models.Follow(follower_id=current_user.id, following_id=user_id)
        db.add(follow)
        db.commit()
        return {"following": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        elif app_type == 'ecommerce':
            return '''from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, auth, database
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="E-Commerce Store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    stock: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[CartItem]
    total: float

# Product Endpoints
@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/api/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Cart Endpoints
@app.post("/api/cart")
def add_to_cart(item: CartItem, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = models.CartItem(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    return {"message": "Added to cart"}

@app.get("/api/cart")
def get_cart(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()

# Order Endpoints
@app.post("/api/orders")
def create_order(order: OrderCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_order = models.Order(
        user_id=current_user.id,
        total=order.total,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item in order.items:
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(order_item)
    
    # Clear cart
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    
    return db_order

@app.get("/api/orders")
def get_orders(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        # Default CRUD app
        return '''from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, auth, database
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ItemCreate(BaseModel):
    title: str
    description: str

@app.post("/api/items")
def create_item(item: ItemCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict(), user_id=current_user.id, created_at=datetime.utcnow())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/api/items")
def get_items(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.user_id == current_user.id).all()

@app.put("/api/items/{item_id}")
def update_item(item_id: int, item: ItemCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.title = item.title
    db_item.description = item.description
    db.commit()
    return db_item

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''