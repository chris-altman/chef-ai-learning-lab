from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from learning_system import LearningSystem, CulinaryMastery

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize learning system
learning_system = LearningSystem()

# Load previous state if exists
try:
    learning_system.load_state("learning_state.json")
except:
    print("No previous learning state found, starting fresh")

class RecipeRequest(BaseModel):
    ingredients: List[str]

class RecipeStep(BaseModel):
    step_number: int
    instruction: str
    time: Optional[str]
    tips: Optional[List[str]]

class Recipe(BaseModel):
    id: int
    recipe_name: str
    description: str
    ingredients: List[Dict[str, str]]
    techniques: List[str]
    steps: List[RecipeStep]
    total_time: str
    difficulty: str
    confidence: float
    suggested_sides: Optional[List[str]]

class LearningFeedback(BaseModel):
    recipe_id: int
    ingredients: List[str]
    techniques: List[str]
    rating: int

def generate_cooking_steps(ingredients: List[str], style: str) -> List[RecipeStep]:
    """Generate detailed cooking steps based on ingredients and style."""
    steps = []
    step_num = 1
    
    # Preparation step
    steps.append(RecipeStep(
        step_number=step_num,
        instruction="Gather and prepare all ingredients",
        time="5-10 minutes",
        tips=[
            "Read through entire recipe first",
            "Set up your workspace with all needed tools",
            "Ensure all ingredients are at room temperature if needed"
        ]
    ))
    step_num += 1

    # Ingredient preparation steps
    if "onions" in ingredients:
        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Dice the onions into small, uniform pieces",
            time="2-3 minutes",
            tips=[
                "Use a sharp knife for clean cuts",
                "Cut end to end for more even pieces",
                "Keep root end intact while cutting for stability"
            ]
        ))
        step_num += 1

    if "beef" in ingredients:
        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Pat the beef dry with paper towels and season generously with salt and pepper",
            time="2-3 minutes",
            tips=[
                "Let meat come to room temperature before cooking",
                "Don't oversalt - you can add more later",
                "Press seasonings into meat slightly"
            ]
        ))
        step_num += 1

        # Add cooking step for beef
        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Heat a large pan over medium-high heat. Once hot, add oil and sear the beef",
            time="3-5 minutes per side",
            tips=[
                "Use a heavy-bottomed pan for even heating",
                "Don't move the meat too much while searing",
                "Look for a golden-brown crust"
            ]
        ))
        step_num += 1

    if "eggs" in ingredients:
        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Crack eggs into a bowl and whisk until just combined",
            time="1-2 minutes",
            tips=[
                "Don't overbeat the eggs",
                "Add a splash of milk for fluffier eggs",
                "Season with salt and pepper"
            ]
        ))
        step_num += 1

    # Style-specific steps
    if style == "sandwich":
        if "bread" in ingredients:
            steps.append(RecipeStep(
                step_number=step_num,
                instruction="Toast the bread slices until golden brown",
                time="2-3 minutes",
                tips=[
                    "Watch carefully to prevent burning",
                    "Butter the bread before toasting for extra flavor",
                    "Toast both sides evenly"
                ]
            ))
            step_num += 1

        # Assembly step
        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Assemble the sandwich with your prepared ingredients",
            time="2-3 minutes",
            tips=[
                "Layer ingredients evenly for balanced bites",
                "Place warm ingredients in the middle",
                "Add condiments last to prevent soggy bread"
            ]
        ))
        step_num += 1

    elif "eggs" in ingredients:
        if "onions" in ingredients:
            steps.append(RecipeStep(
                step_number=step_num,
                instruction="Sauté the diced onions until translucent",
                time="3-4 minutes",
                tips=[
                    "Use medium heat to avoid burning",
                    "Stir occasionally for even cooking",
                    "A pinch of salt helps release moisture"
                ]
            ))
            step_num += 1

        steps.append(RecipeStep(
            step_number=step_num,
            instruction="Add beaten eggs to the pan and cook, stirring gently",
            time="2-3 minutes",
            tips=[
                "Keep heat at medium-low",
                "Stir occasionally for creamy eggs",
                "Remove from heat just before fully set - they'll continue cooking"
            ]
        ))
        step_num += 1

    # Final step
    final_instruction = "Plate your dish"
    if "ketchup" in ingredients:
        final_instruction += " and add ketchup to taste"
    
    steps.append(RecipeStep(
        step_number=step_num,
        instruction=final_instruction + ". Serve immediately.",
        time="1 minute",
        tips=[
            "Garnish with fresh herbs if available",
            "Serve while hot for best results",
            "Add final seasonings if needed"
        ]
    ))

    return steps

@app.post("/api/generate_recipe", response_model=Recipe)
async def generate_recipe(request: RecipeRequest):
    ingredients = request.ingredients
    
    # Determine cooking style based on ingredients
    has_bread = "bread" in ingredients
    has_beef = "beef" in ingredients
    has_eggs = "eggs" in ingredients
    
    if has_bread and (has_beef or has_eggs):
        style = "sandwich"
    elif has_eggs:
        style = "egg_dish"
    else:
        style = "general"

    # Generate basic recipe info
    recipe_name = f"Homestyle {style.title()} with {', '.join(ingredients[:2]).title()}"
    description = f"A delicious {style.lower()} featuring {', '.join(ingredients)}"
    
    # Format ingredients with measurements
    formatted_ingredients = []
    for ing in ingredients:
        if ing == "beef":
            amount = "6 ounces"
            prep = "sliced or patty form"
        elif ing == "eggs":
            amount = "2 large"
            prep = "beaten"
        elif ing == "onions":
            amount = "1 medium"
            prep = "diced"
        elif ing == "bread":
            amount = "2 slices"
            prep = "toasted"
        else:
            amount = "to taste"
            prep = ""
            
        formatted_ingredients.append({
            "item": ing,
            "amount": amount,
            "preparation": prep
        })

    # Generate detailed steps
    steps = generate_cooking_steps(ingredients, style)
    
    # Calculate total time
    total_minutes = sum(
        int(step.time.split("-")[0]) if step.time else 0 
        for step in steps
    )
    max_minutes = sum(
        int(step.time.split("-")[1].split()[0]) if step.time and "-" in step.time else 0
        for step in steps
    )
    total_time = f"{total_minutes}-{max_minutes} minutes"

    # Determine techniques based on steps
    techniques = []
    if "beef" in ingredients:
        techniques.extend(["searing", "seasoning"])
    if "eggs" in ingredients:
        techniques.extend(["whisking", "scrambling"])
    if "onions" in ingredients:
        techniques.append("dicing")
    techniques = list(set(techniques))  # Remove duplicates

    # Get learning system confidence
    learning_status = learning_system.get_learning_status()
    confidence = min(0.95, 0.7 + learning_status["overall_mastery"])

    # Create recipe
    recipe = Recipe(
        id=len(learning_system.known_recipes) + 1,
        recipe_name=recipe_name,
        description=description,
        ingredients=formatted_ingredients,
        techniques=techniques,
        steps=steps,
        total_time=total_time,
        difficulty="Easy" if len(steps) <= 5 else "Medium" if len(steps) <= 8 else "Hard",
        confidence=confidence,
        suggested_sides=["Fresh salad", "Steamed vegetables"] if style != "sandwich" else ["Potato chips", "Pickle spear"]
    )

    # Save state
    learning_system.save_state("learning_state.json")
    
    return recipe

@app.get("/api/learning_stats")
async def get_learning_stats():
    return learning_system.get_learning_status()

@app.post("/api/learn")
async def learn_from_feedback(feedback: LearningFeedback):
    # Create recipe object for evaluation
    recipe = {
        "id": feedback.recipe_id,
        "ingredients": [{"item": ing} for ing in feedback.ingredients],
        "techniques": feedback.techniques,
        "steps": []  # Steps aren't needed for feedback evaluation
    }
    
    # Process feedback
    changes = learning_system.evaluate_recipe_success(recipe, {"rating": feedback.rating})
    
    # Save updated state
    learning_system.save_state("learning_state.json")
    
    return {
        "message": "Feedback recorded successfully",
        "mastery_changes": changes
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
