from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from backend.learning.core import ChefAI

app = FastAPI(title="Chef AI Learning Lab API")
chef_ai = ChefAI()

class RecipeInput(BaseModel):
    ingredients: List[str]
    techniques: Optional[List[str]] = []
    rating: Optional[float] = None
    feedback: Optional[str] = None

class RecipeOutput(BaseModel):
    recipe_name: str
    ingredients: List[str]
    techniques: List[str]
    steps: List[str]
    difficulty: str
    confidence: float
    estimated_time: int  # minutes

@app.post("/api/generate_recipe")
async def generate_recipe(input_data: RecipeInput) -> RecipeOutput:
    """Generate a recipe based on available ingredients"""
    try:
        recipe = chef_ai.generate_recipe(input_data.ingredients)
        return RecipeOutput(**recipe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learn")
async def learn_from_feedback(input_data: RecipeInput):
    """Learn from user feedback about a recipe"""
    if input_data.rating is None:
        raise HTTPException(status_code=400, detail="Rating is required for learning")
    
    try:
        recipe_data = {
            'ingredients': input_data.ingredients,
            'techniques': input_data.techniques,
            'rating': input_data.rating,
            'feedback': input_data.feedback,
            'timestamp': datetime.now().isoformat()
        }
        chef_ai.learn(recipe_data)
        return {"status": "success", "message": "Learning updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skill_level")
async def get_skill_level():
    """Get current AI skill level"""
    try:
        level = chef_ai.complexity_manager.get_current_skill_level()
        progress = chef_ai.complexity_manager.current_level
        return {
            "level": level,
            "progress": progress,
            "history": chef_ai.complexity_manager.progression_history[-10:]  # Last 10 entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ingredient_compatibility/{ingredient}")
async def get_compatibility(ingredient: str):
    """Get compatibility scores for an ingredient"""
    try:
        scores = chef_ai.ingredient_learner.compatibility_matrix[ingredient]
        return {
            "ingredient": ingredient,
            "compatibility_scores": dict(scores),
            "confidence_scores": dict(chef_ai.ingredient_learner.confidence_scores[ingredient])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning_stats")
async def get_learning_stats():
    """Get overall learning statistics"""
    return {
        "total_recipes_learned": len(chef_ai.recipe_learner.successful_patterns),
        "known_ingredients": len(chef_ai.ingredient_learner.ingredient_vectors),
        "known_techniques": len(chef_ai.recipe_learner.technique_graph.nodes),
        "flavor_combinations": len(chef_ai.flavor_learner.successful_combinations)
    }
