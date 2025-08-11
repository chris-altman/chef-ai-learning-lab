from typing import List, Dict, Tuple
import numpy as np
from sklearn.manifold import TSNE
import torch
import torch.nn as nn
import networkx as nx
from collections import defaultdict

class IngredientEmbedding(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.fc = nn.Linear(embedding_dim, embedding_dim)
        
    def forward(self, x):
        x = self.embedding(x)
        return torch.tanh(self.fc(x))

class ChefAI:
    def __init__(self):
        self.ingredient_learner = IngredientLearner()
        self.recipe_learner = RecipeLearner()
        self.flavor_learner = FlavorLearner()
        self.complexity_manager = ComplexityManager()
        
    def learn(self, recipe_data: Dict):
        """Integrated learning from all components"""
        ingredients = recipe_data['ingredients']
        techniques = recipe_data['techniques']
        rating = recipe_data['rating']
        
        # Update all learning components
        self.ingredient_learner.learn_from_feedback(ingredients, rating)
        self.recipe_learner.learn_technique_sequence(techniques, rating)
        self.flavor_learner.update_flavor_knowledge(ingredients, rating)
        self.complexity_manager.update_complexity(recipe_data)
        
    def generate_recipe(self, available_ingredients: List[str]) -> Dict:
        """Generate a recipe using all learned components"""
        # Get compatible ingredients
        ingredient_scores = self.ingredient_learner.get_compatibility_scores(available_ingredients)
        
        # Get appropriate techniques
        suitable_techniques = self.recipe_learner.suggest_techniques(
            self.complexity_manager.current_level
        )
        
        # Consider flavor profiles
        flavor_suggestions = self.flavor_learner.suggest_combinations(available_ingredients)
        
        # Integrate all components for final recipe
        return self._create_recipe(ingredient_scores, suitable_techniques, flavor_suggestions)

class IngredientLearner:
    def __init__(self):
        self.compatibility_matrix = defaultdict(lambda: defaultdict(float))
        self.confidence_scores = defaultdict(lambda: defaultdict(lambda: 1.0))
        self.embedding_model = None
        self.ingredient_vectors = {}
        
    def learn_from_feedback(self, ingredients: List[str], rating: float):
        """Update compatibility scores using Bayesian update"""
        for i1 in ingredients:
            for i2 in ingredients:
                if i1 != i2:
                    current_score = self.compatibility_matrix[i1][i2]
                    confidence = self.confidence_scores[i1][i2]
                    
                    # Bayesian update
                    new_score = (current_score * confidence + rating) / (confidence + 1)
                    new_confidence = confidence + 1
                    
                    self.compatibility_matrix[i1][i2] = new_score
                    self.confidence_scores[i1][i2] = new_confidence
                    
        # Update embeddings
        self._update_embeddings(ingredients, rating)
    
    def _update_embeddings(self, ingredients: List[str], rating: float):
        """Update ingredient embeddings based on co-occurrence"""
        if not self.embedding_model:
            # Initialize embedding model if needed
            vocab_size = len(self.ingredient_vectors) + len(ingredients)
            self.embedding_model = IngredientEmbedding(vocab_size)
            
        # Update embeddings using the rating as a weight
        # Implementation would use PyTorch for actual training

class RecipeLearner:
    def __init__(self):
        self.technique_graph = nx.DiGraph()
        self.technique_difficulties = {}
        self.successful_patterns = []
        
    def learn_technique_sequence(self, techniques: List[str], success_rating: float):
        """Learn successful technique combinations and their order"""
        if success_rating > 0.7:  # Only learn from successful recipes
            for i in range(len(techniques) - 1):
                current, next_tech = techniques[i], techniques[i + 1]
                
                # Update technique graph
                if not self.technique_graph.has_edge(current, next_tech):
                    self.technique_graph.add_edge(current, next_tech, weight=1)
                else:
                    self.technique_graph[current][next_tech]['weight'] += 1
                    
                # Update difficulty ratings
                self._update_difficulty(current, next_tech, success_rating)
    
    def _update_difficulty(self, tech1: str, tech2: str, rating: float):
        """Update the difficulty assessment of technique combinations"""
        current_diff = self.technique_difficulties.get((tech1, tech2), 0.5)
        self.technique_difficulties[(tech1, tech2)] = (current_diff + rating) / 2

class FlavorLearner:
    def __init__(self):
        self.flavor_profiles = {}
        self.successful_combinations = []
        self.taste_model = None
        
    def update_flavor_knowledge(self, ingredients: List[str], rating: float):
        """Learn flavor compatibility and taste profiles"""
        # Extract or create flavor vectors
        vectors = [self._get_flavor_vector(ing) for ing in ingredients]
        
        if rating > 0.8:  # High-rated combinations
            self.successful_combinations.append(ingredients)
            
        # Update flavor space
        self._update_flavor_space(vectors, rating)
    
    def _get_flavor_vector(self, ingredient: str) -> np.ndarray:
        """Get or initialize flavor vector for ingredient"""
        if ingredient not in self.flavor_profiles:
            # Initialize with random vector
            self.flavor_profiles[ingredient] = np.random.randn(64)
        return self.flavor_profiles[ingredient]
    
    def _update_flavor_space(self, vectors: List[np.ndarray], rating: float):
        """Update flavor space using TSNE for dimensionality reduction"""
        if len(vectors) > 1:
            tsne = TSNE(n_components=2, random_state=42)
            embedded_vectors = tsne.fit_transform(np.array(vectors))
            # Update flavor profiles based on embedding
            # Implementation would use the rating to weight updates

class ComplexityManager:
    def __init__(self):
        self.current_level = 0
        self.progression_history = []
        self.skill_thresholds = {
            0: "Beginner",
            20: "Intermediate",
            40: "Advanced",
            60: "Expert",
            80: "Master"
        }
    
    def update_complexity(self, recipe_data: Dict):
        """Update complexity level based on success with current level"""
        success_rate = recipe_data.get('rating', 0)
        technique_count = len(recipe_data.get('techniques', []))
        
        # Adjust level based on performance
        if success_rate > 0.8 and technique_count >= self.current_level / 10:
            self.current_level = min(100, self.current_level + 5)
        elif success_rate < 0.3:
            self.current_level = max(0, self.current_level - 2)
            
        self.progression_history.append({
            'level': self.current_level,
            'success_rate': success_rate,
            'timestamp': recipe_data.get('timestamp')
        })
    
    def get_current_skill_level(self) -> str:
        """Get the current skill level description"""
        for threshold, level in sorted(self.skill_thresholds.items(), reverse=True):
            if self.current_level >= threshold:
                return level
        return "Beginner"
