from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(JSON)  # List of ingredients
    techniques = Column(JSON)   # List of techniques
    difficulty = Column(String)
    confidence = Column(Float)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(String, nullable=True)

class LearningProgress(Base):
    __tablename__ = 'learning_progress'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    skill_level = Column(Float)
    known_ingredients = Column(Integer)
    known_techniques = Column(Integer)
    successful_combinations = Column(Integer)

class IngredientCompatibility(Base):
    __tablename__ = 'ingredient_compatibility'
    
    id = Column(Integer, primary_key=True)
    ingredient1 = Column(String)
    ingredient2 = Column(String)
    compatibility_score = Column(Float)
    confidence_score = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

class FlavorProfile(Base):
    __tablename__ = 'flavor_profiles'
    
    id = Column(Integer, primary_key=True)
    ingredient = Column(String, unique=True)
    vector = Column(JSON)  # Store the vector as JSON
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create database engine
engine = create_engine('sqlite:///chef_ai.db')

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
