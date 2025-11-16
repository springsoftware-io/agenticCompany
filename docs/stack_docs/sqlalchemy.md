# SQLAlchemy Documentation

**Official Docs:** https://docs.sqlalchemy.org/

## Overview
SQLAlchemy is a Python SQL toolkit and ORM. We use SQLAlchemy 2.0 for database operations in the Seed Planter API.

## Key Features
- ORM (Object-Relational Mapping)
- Connection pooling
- Transaction management
- Query builder
- Database migrations (with Alembic)
- Multiple database support

## Installation

```bash
pip install sqlalchemy psycopg2-binary
```

## Database Connection

### Create Engine
```python
from sqlalchemy import create_engine

# PostgreSQL
engine = create_engine(
    "postgresql://user:password@localhost/dbname",
    echo=True,  # Log SQL queries
    pool_size=5,
    max_overflow=10
)

# SQLite
engine = create_engine("sqlite:///database.db")
```

### Session Management
```python
from sqlalchemy.orm import sessionmaker, Session

SessionLocal = sessionmaker(bind=engine)

# Use session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Define Models

### Basic Model
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"
```

### Relationships
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    
    # One-to-many
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Many-to-one
    author = relationship("User", back_populates="posts")
```

### Many-to-Many
```python
from sqlalchemy import Table

# Association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    users = relationship("User", secondary=user_roles, back_populates="roles")
```

## Create Tables

```python
# Create all tables
Base.metadata.create_all(bind=engine)

# Drop all tables
Base.metadata.drop_all(bind=engine)
```

## CRUD Operations

### Create
```python
from sqlalchemy.orm import Session

def create_user(db: Session, username: str, email: str):
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)  # Get updated data (like auto-generated ID)
    return user

# Bulk insert
users = [
    User(username="alice", email="alice@example.com"),
    User(username="bob", email="bob@example.com")
]
db.add_all(users)
db.commit()
```

### Read
```python
# Get by ID
user = db.query(User).filter(User.id == 1).first()

# Get all
users = db.query(User).all()

# Filter
users = db.query(User).filter(User.username == "john").all()

# Multiple filters
users = db.query(User).filter(
    User.username == "john",
    User.email.like("%@example.com")
).all()

# Order by
users = db.query(User).order_by(User.created_at.desc()).all()

# Limit and offset
users = db.query(User).limit(10).offset(20).all()

# Count
count = db.query(User).count()

# First or None
user = db.query(User).filter(User.id == 999).first()  # Returns None if not found
```

### Update
```python
# Update single record
user = db.query(User).filter(User.id == 1).first()
user.email = "newemail@example.com"
db.commit()

# Bulk update
db.query(User).filter(User.active == False).update({"active": True})
db.commit()
```

### Delete
```python
# Delete single record
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()

# Bulk delete
db.query(User).filter(User.active == False).delete()
db.commit()
```

## Advanced Queries

### Joins
```python
# Inner join
results = db.query(User, Post).join(Post).all()

# Left outer join
results = db.query(User).outerjoin(Post).all()

# Explicit join condition
results = db.query(User).join(Post, User.id == Post.user_id).all()
```

### Aggregations
```python
from sqlalchemy import func

# Count
count = db.query(func.count(User.id)).scalar()

# Sum
total = db.query(func.sum(Order.total)).scalar()

# Average
avg_price = db.query(func.avg(Product.price)).scalar()

# Group by
results = db.query(
    User.username,
    func.count(Post.id)
).join(Post).group_by(User.username).all()
```

### Subqueries
```python
from sqlalchemy import select

# Subquery
subq = db.query(func.avg(Product.price)).scalar_subquery()
expensive_products = db.query(Product).filter(Product.price > subq).all()
```

## Transactions

```python
# Manual transaction
try:
    user = User(username="john", email="john@example.com")
    db.add(user)
    db.commit()
except Exception as e:
    db.rollback()
    raise e
finally:
    db.close()

# Context manager
with Session(engine) as session:
    user = User(username="john", email="john@example.com")
    session.add(user)
    session.commit()
```

## Async Support (SQLAlchemy 2.0)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

# Create async engine
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    echo=True
)

# Create async session
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Use async session
async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).filter(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

## Alembic Migrations

### Setup
```bash
pip install alembic
alembic init alembic
```

### Configuration
```python
# alembic/env.py
from myapp.models import Base

target_metadata = Base.metadata
```

### Create Migration
```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add users table"

# Manual migration
alembic revision -m "Add column"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

## FastAPI Integration

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use in endpoint
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

## Best Practices

1. **Use sessions properly** - always close them
2. **Use connection pooling** for better performance
3. **Use indexes** on frequently queried columns
4. **Lazy load relationships** by default
5. **Use transactions** for data consistency
6. **Use Alembic** for database migrations
7. **Avoid N+1 queries** - use eager loading
8. **Use `refresh()`** after commit to get updated data
9. **Handle exceptions** and rollback on errors
10. **Use async** for high-concurrency applications

## Common Patterns

### Eager Loading
```python
from sqlalchemy.orm import joinedload

# Avoid N+1 queries
users = db.query(User).options(joinedload(User.posts)).all()
```

### Pagination
```python
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
```

### Soft Delete
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    deleted_at = Column(DateTime, nullable=True)

# Soft delete
user.deleted_at = datetime.utcnow()
db.commit()

# Query only active
active_users = db.query(User).filter(User.deleted_at.is_(None)).all()
```

## Resources
- Official Docs: https://docs.sqlalchemy.org/
- Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- ORM Guide: https://docs.sqlalchemy.org/en/20/orm/
- Alembic Docs: https://alembic.sqlalchemy.org/

## Version Used in SeedGPT
```
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
```
