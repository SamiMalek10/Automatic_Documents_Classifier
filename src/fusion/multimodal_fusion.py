import numpy as np
from config.config import FUSION_CONFIG, CLASSES
import logging

class MultimodalFusion:
    """Fusion intelligente des prédictions CV et NLP"""
    
    def __init__(self):
        self.config = FUSION_CONFIG
        self.logger = logging.getLogger(__name__)
    
    def perfect_agreement(self, cv_pred, nlp_pred, cv_conf, nlp_conf):
        """Vérifie si CV et NLP sont d'accord"""
        if cv_pred == nlp_pred:
            threshold = self.config['perfect_agreement_threshold']
            if cv_conf > threshold and nlp_conf > threshold:
                avg_conf = (cv_conf + nlp_conf) / 2
                return True, cv_pred, avg_conf
        
        return False, None, 0.0
    
    def strong_cv_decision(self, cv_pred, cv_conf, template_score):
        """CV très confiant + gabarits valident"""
        cv_threshold = self.config['strong_cv_threshold']
        template_threshold = self.config['template_validation_threshold']
        
        if cv_conf > cv_threshold and template_score > template_threshold:
            # Confiance combinée
            combined_conf = (cv_conf * 0.7 + template_score * 0.3)
            return True, cv_pred, combined_conf
        
        return False, None, 0.0
    
    def strong_nlp_decision(self, nlp_pred, nlp_conf, pattern_strength):
        """NLP très confiant + motifs textuels forts"""
        nlp_threshold = self.config['strong_nlp_threshold']
        
        if nlp_conf > nlp_threshold and pattern_strength > 0.7:
            combined_conf = (nlp_conf * 0.8 + pattern_strength * 0.2)
            return True, nlp_pred, combined_conf
        
        return False, None, 0.0
    
    def weighted_voting(self, cv_pred, nlp_pred, cv_conf, nlp_conf, 
                       template_score, pattern_strength):
        """Vote pondéré quand les approches divergent"""
        
        # Calcul des scores finaux pour chaque approche
        cv_final_score = cv_conf * 0.6 + template_score * 0.4
        nlp_final_score = nlp_conf * 0.7 + pattern_strength * 0.3
        
        # Décision
        if cv_final_score > nlp_final_score:
            return cv_pred, cv_final_score
        else:
            return nlp_pred, nlp_final_score
    
    def apply_business_rules(self, pred_class, features, text_patterns):
        """Validation par règles métier"""
        violations = []
        
        if pred_class == "identite":
            # Doit avoir une photo ET format carte
            if not features.get('has_photo', False):
                violations.append("Pas de photo détectée pour une pièce d'identité")
            
            aspect_ratio = features.get('aspect_ratio', 0)
            if not (1.5 <= aspect_ratio <= 1.7):
                violations.append("Format non conforme à une carte d'identité")
        
        elif pred_class == "releve_bancaire":
            # Doit avoir structure tabulaire ET montants
            if not features.get('has_table', False):
                violations.append("Pas de structure tabulaire pour un relevé")
            
            if not text_patterns.get('montants'):
                violations.append("Pas de montants détectés")
        
        elif pred_class == "facture_electricite":
            # Doit avoir kWh
            if text_patterns.get('kwh', 0) == 0:
                violations.append("Pas d'unité kWh détectée")
        
        elif pred_class == "facture_eau":
            # Doit avoir m³
            if text_patterns.get('m3', 0) == 0:
                violations.append("Pas d'unité m³ détectée")
        
        elif pred_class == "document_employeur":
            # Doit avoir mentions salariales
            if not text_patterns.get('montants'):
                violations.append("Pas de montants salariaux détectés")
        
        return len(violations) == 0, violations
    
    def fuse(self, cv_result, nlp_result, template_features, text_patterns):
        """
        Fonction principale de fusion
        
        Args:
            cv_result: (predicted_class, confidence)
            nlp_result: (predicted_class, confidence, pattern_strength)
            template_features: dict des features de gabarits
            text_patterns: dict des patterns textuels extraits
        
        Returns:
            (final_class, final_confidence, decision_path, should_reject)
        """
        
        cv_pred, cv_conf = cv_result
        nlp_pred, nlp_conf, pattern_strength = nlp_result
        
        # Score du gabarit pour la classe prédite par CV
        template_score = template_features.get('template_scores', {}).get(cv_pred, 0.0)
        
        # 1. Accord parfait
        is_perfect, pred, conf = self.perfect_agreement(cv_pred, nlp_pred, cv_conf, nlp_conf)
        if is_perfect:
            valid, violations = self.apply_business_rules(pred, template_features, text_patterns)
            
            if valid:
                return pred, conf, "perfect_agreement", False
            else:
                self.logger.warning(f"Violations règles métier: {violations}")
                return pred, conf * 0.7, "perfect_agreement_with_violations", False
        
        # 2. CV fort + gabarits
        is_strong_cv, pred, conf = self.strong_cv_decision(cv_pred, cv_conf, template_score)
        if is_strong_cv:
            valid, violations = self.apply_business_rules(pred, template_features, text_patterns)
            
            if valid:
                return pred, conf, "strong_cv_validated", False
            else:
                # Réduire confiance mais ne pas rejeter
                return pred, conf * 0.6, "strong_cv_with_violations", False
        
        # 3. NLP fort + patterns
        is_strong_nlp, pred, conf = self.strong_nlp_decision(nlp_pred, nlp_conf, pattern_strength)
        if is_strong_nlp:
            valid, violations = self.apply_business_rules(pred, template_features, text_patterns)
            
            if valid:
                return pred, conf, "strong_nlp_validated", False
            else:
                return pred, conf * 0.6, "strong_nlp_with_violations", False
        
        # 4. Vote pondéré
        pred, conf = self.weighted_voting(
            cv_pred, nlp_pred, cv_conf, nlp_conf, 
            template_score, pattern_strength
        )
        
        # 5. Décision de rejet
        rejection_threshold = self.config['rejection_threshold']
        should_reject = conf < rejection_threshold
        
        if should_reject:
            return pred, conf, "weighted_voting_rejected", True
        else:
            valid, violations = self.apply_business_rules(pred, template_features, text_patterns)
            
            if not valid:
                conf *= 0.5
                should_reject = conf < rejection_threshold
            
            return pred, conf, "weighted_voting", should_reject