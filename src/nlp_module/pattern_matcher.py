import re
from collections import Counter
import numpy as np
from src.config.config import KEYWORDS, CLASSES

class PatternMatcher:
    """Classification par motifs sémantiques"""
    
    def __init__(self):
        self.keywords = KEYWORDS
        self.classes = CLASSES
    
    def preprocess_text(self, text):
        """Nettoie et normalise le texte"""
        # Minuscules
        text = text.lower()
        
        # Suppression de la ponctuation excessive
        text = re.sub(r'[^\w\s€°³]', ' ', text)
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text):
        """Extrait les mots-clés trouvés par classe"""
        text = self.preprocess_text(text)
        
        found_keywords = {cls: [] for cls in self.classes}
        
        for cls in self.classes:
            for keyword in self.keywords[cls]:
                keyword_lower = keyword.lower()
                # Compte les occurrences
                count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text))
                if count > 0:
                    found_keywords[cls].append((keyword, count))
        
        return found_keywords
    
    def compute_class_scores(self, text):
        """Calcule un score pour chaque classe"""
        found = self.extract_keywords(text)
        
        scores = {}
        
        for cls in self.classes:
            if not found[cls]:
                scores[cls] = 0.0
                continue
            
            # Score = somme pondérée des occurrences
            total_score = 0
            for keyword, count in found[cls]:
                # Mots plus longs = plus spécifiques = poids plus important
                weight = len(keyword) / 10.0
                total_score += count * weight
            
            # Normalisation
            scores[cls] = min(total_score / 10.0, 1.0)
        
        return scores
    
    
    def predict(self, text):
        """Prédit la classe et retourne la confiance + scores détaillés"""
        scores = self.compute_class_scores(text)
        
        # Vérifie si tous les scores sont nuls
        if not scores or max(scores.values()) == 0:
            # Retourne TOUJOURS 3 éléments, même en cas d'échec
            return None, 0.0, {cls: 0.0 for cls in self.classes}
        
        # Classe avec le score max
        predicted_class = max(scores, key=scores.get)
        confidence = scores[predicted_class]
        
        return predicted_class, confidence, scores
    def extract_specific_patterns(self, text):
        """Extrait des patterns spécifiques (montants, dates, unités)"""
        patterns = {
            'montants': re.findall(r'\d+[,.]?\d*\s*(?:dh|mad|€)', text.lower()),
            'kwh': len(re.findall(r'kwh', text.lower())),
            'm3': len(re.findall(r'm[³3]', text.lower())),
            'dates': len(re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)),
            'cin': len(re.findall(r'[a-z]{1,2}\d{5,7}', text.lower())),
            'rib': len(re.findall(r'\d{24}', text))
        }
        
        return patterns