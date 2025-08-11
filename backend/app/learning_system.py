from typing import Dict, List, Set, Optional
import json
from datetime import datetime
from enum import Enum
import math

class CulinaryMastery:
    """Tracks different aspects of culinary knowledge and skill"""
    
    class SkillCategory(Enum):
        TECHNIQUE_MASTERY = "technique_mastery"
        FLAVOR_PAIRING = "flavor_pairing"
        TIMING_CONTROL = "timing_control"
        INGREDIENT_KNOWLEDGE = "ingredient_knowledge"
        RECIPE_COMPLEXITY = "recipe_complexity"
        SEASONING_EXPERTISE = "seasoning_expertise"
        TEMPERATURE_CONTROL = "temperature_control"
        PRESENTATION = "presentation"
        
    def __init__(self):
        self.categories = {category: 0.0 for category in self.SkillCategory}
        self.learning_history = []
        self.experimentation_outcomes = []
        self.successful_innovations = set()
        
    def calculate_overall_mastery(self) -> float:
        """Calculate overall mastery level based on all categories"""
        return sum(self.categories.values()) / len(self.categories)

class LearningSystem:
    def __init__(self):
        self.mastery = CulinaryMastery()
        self.known_recipes: Dict[str, Dict] = {}  # Recipe name -> details
        self.ingredient_relationships: Dict[str, Set[str]] = {}
        self.technique_proficiency: Dict[str, float] = {}
        self.flavor_combinations: Dict[str, Dict[str, int]] = {}  # Ingredient -> {paired_ingredient -> success_count}
        self.innovation_attempts: List[Dict] = []  # Track experimental combinations
        self.feedback_history: List[Dict] = []
        
    def evaluate_recipe_success(self, recipe: Dict, feedback: Dict) -> Dict[str, float]:
        """
        Evaluate recipe success and update mastery levels based on complexity and feedback
        Returns changes in mastery levels
        """
        changes = {category.value: 0.0 for category in CulinaryMastery.SkillCategory}
        
        # Analyze recipe complexity
        complexity_score = self._calculate_complexity(recipe)
        
        # Evaluate technique usage
        if feedback["rating"] == 1:  # Positive feedback
            for technique in recipe["techniques"]:
                if technique not in self.technique_proficiency:
                    self.technique_proficiency[technique] = 0.1
                self.technique_proficiency[technique] = min(1.0, 
                    self.technique_proficiency[technique] + (0.1 * complexity_score))
                changes[CulinaryMastery.SkillCategory.TECHNIQUE_MASTERY.value] += 0.05
        
        # Update flavor pairing knowledge
        ingredients = recipe["ingredients"]
        for i in range(len(ingredients)):
            for j in range(i + 1, len(ingredients)):
                ing1, ing2 = ingredients[i]["item"], ingredients[j]["item"]
                self._update_flavor_pairing(ing1, ing2, feedback["rating"])
        
        # Evaluate innovation
        if self._is_novel_combination(recipe):
            changes[CulinaryMastery.SkillCategory.RECIPE_COMPLEXITY.value] += 0.1
            if feedback["rating"] == 1:
                self.successful_innovations.add(
                    frozenset([ing["item"] for ing in recipe["ingredients"]])
                )
        
        # Update mastery levels based on feedback and complexity
        self._update_mastery_levels(changes, complexity_score, feedback)
        
        return changes
    
    def _calculate_complexity(self, recipe: Dict) -> float:
        """Calculate recipe complexity score based on various factors"""
        complexity = 0.0
        
        # Number of ingredients
        num_ingredients = len(recipe["ingredients"])
        complexity += min(1.0, num_ingredients / 10.0)
        
        # Number of techniques
        num_techniques = len(recipe["techniques"])
        complexity += min(1.0, num_techniques / 5.0)
        
        # Number of steps
        num_steps = len(recipe["steps"])
        complexity += min(1.0, num_steps / 15.0)
        
        # Timing complexity
        total_time = sum(int(step.time.split("-")[0]) for step in recipe["steps"] if step.time)
        complexity += min(1.0, total_time / 60.0)  # Normalize to 1 hour
        
        return complexity / 4.0  # Average of all factors
    
    def _update_flavor_pairing(self, ing1: str, ing2: str, success: int):
        """Update knowledge about flavor combinations"""
        if ing1 not in self.flavor_combinations:
            self.flavor_combinations[ing1] = {}
        if ing2 not in self.flavor_combinations:
            self.flavor_combinations[ing2] = {}
            
        if ing2 not in self.flavor_combinations[ing1]:
            self.flavor_combinations[ing1][ing2] = 0
        if ing1 not in self.flavor_combinations[ing2]:
            self.flavor_combinations[ing2][ing1] = 0
            
        change = 1 if success == 1 else -0.5
        self.flavor_combinations[ing1][ing2] += change
        self.flavor_combinations[ing2][ing1] += change
    
    def _is_novel_combination(self, recipe: Dict) -> bool:
        """Determine if this is a novel ingredient/technique combination"""
        ingredients = frozenset([ing["item"] for ing in recipe["ingredients"]])
        techniques = frozenset(recipe["techniques"])
        
        # Check if this exact combination exists in our history
        combination = (ingredients, techniques)
        is_novel = combination not in self.known_recipes
        
        if is_novel:
            self.known_recipes[str(combination)] = {
                "first_attempted": datetime.now().isoformat(),
                "times_attempted": 1
            }
        else:
            self.known_recipes[str(combination)]["times_attempted"] += 1
            
        return is_novel
    
    def _update_mastery_levels(self, changes: Dict[str, float], complexity: float, feedback: Dict):
        """Update mastery levels based on recipe outcome"""
        feedback_multiplier = 1.0 if feedback["rating"] == 1 else -0.5
        
        for category in CulinaryMastery.SkillCategory:
            current_level = self.mastery.categories[category]
            
            # Calculate learning rate based on current level
            # Learning slows down as mastery increases
            learning_rate = 0.1 * (1.0 - current_level)
            
            # Apply changes with complexity bonus
            change = changes[category.value] * complexity * feedback_multiplier * learning_rate
            
            # Update mastery level with bounds
            self.mastery.categories[category] = max(0.0, min(1.0, current_level + change))
    
    def get_learning_status(self) -> Dict:
        """Get detailed learning status and progress"""
        return {
            "overall_mastery": self.mastery.calculate_overall_mastery(),
            "category_mastery": {
                category.value: self.mastery.categories[category]
                for category in CulinaryMastery.SkillCategory
            },
            "technique_proficiency": self.technique_proficiency,
            "known_combinations": len(self.known_recipes),
            "successful_innovations": len(self.successful_innovations),
            "flavor_expertise": {
                ing: len([v for v in pairs.values() if v > 0])
                for ing, pairs in self.flavor_combinations.items()
            }
        }
    
    def suggest_experiments(self) -> List[Dict]:
        """Suggest new combinations to try based on current knowledge"""
        experiments = []
        
        # Find successful ingredients that haven't been combined
        for ing1 in self.flavor_combinations:
            successful_pairs = [
                ing2 for ing2, score in self.flavor_combinations[ing1].items()
                if score > 0
            ]
            
            # Look for transitive relationships
            # If A works with B, and B works with C, maybe A works with C
            for ing2 in successful_pairs:
                for ing3, score in self.flavor_combinations.get(ing2, {}).items():
                    if (score > 0 and ing3 not in self.flavor_combinations[ing1]
                        and ing3 != ing1):
                        experiments.append({
                            "ingredients": [ing1, ing3],
                            "reasoning": f"Based on mutual success with {ing2}",
                            "confidence": min(
                                self.flavor_combinations[ing1][ing2],
                                self.flavor_combinations[ing2][ing3]
                            ) / 10.0
                        })
        
        return sorted(experiments, key=lambda x: x["confidence"], reverse=True)
    
    def save_state(self, filepath: str):
        """Save learning system state to file"""
        state = {
            "mastery": {
                "categories": {k.value: v for k, v in self.mastery.categories.items()},
                "learning_history": self.mastery.learning_history,
                "successful_innovations": list(self.mastery.successful_innovations)
            },
            "known_recipes": self.known_recipes,
            "ingredient_relationships": {k: list(v) for k, v in self.ingredient_relationships.items()},
            "technique_proficiency": self.technique_proficiency,
            "flavor_combinations": self.flavor_combinations,
            "innovation_attempts": self.innovation_attempts,
            "feedback_history": self.feedback_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f)
    
    def load_state(self, filepath: str):
        """Load learning system state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Restore mastery state
            self.mastery.categories = {
                CulinaryMastery.SkillCategory(k): v 
                for k, v in state["mastery"]["categories"].items()
            }
            self.mastery.learning_history = state["mastery"]["learning_history"]
            self.mastery.successful_innovations = set(state["mastery"]["successful_innovations"])
            
            # Restore other state
            self.known_recipes = state["known_recipes"]
            self.ingredient_relationships = {k: set(v) for k, v in state["ingredient_relationships"].items()}
            self.technique_proficiency = state["technique_proficiency"]
            self.flavor_combinations = state["flavor_combinations"]
            self.innovation_attempts = state["innovation_attempts"]
            self.feedback_history = state["feedback_history"]
        except Exception as e:
            print(f"Error loading learning system state: {e}")
