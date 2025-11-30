import pytesseract
import cv2
import numpy as np
import logging

class OCRExtractor:
    """Extraction de texte via Tesseract OCR"""
    
    def __init__(self, lang='fra'):
        self.lang = lang
        self.logger = logging.getLogger(__name__)
        
        # Configuration Tesseract
        self.config = '--oem 3 --psm 6'  # LSTM + assume uniform block of text
    
    def extract_text(self, image):
        """Extrait le texte d'une image"""
        try:
            text = pytesseract.image_to_string(
                image, 
                lang=self.lang, 
                config=self.config
            )
            
            self.logger.info(f"✅ Texte extrait: {len(text)} caractères")
            return text
        
        except Exception as e:
            self.logger.error(f"❌ Erreur OCR: {e}")
            return ""
    
    def extract_with_confidence(self, image):
        """Extrait le texte avec scores de confiance"""
        try:
            data = pytesseract.image_to_data(
                image, 
                lang=self.lang, 
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Filtrer les mots avec confiance > 60
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > 60:
                    text = data['text'][i]
                    if text.strip():
                        text_parts.append(text)
                        confidences.append(int(conf))
            
            full_text = ' '.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0
            
            return full_text, avg_confidence / 100.0
        
        except Exception as e:
            self.logger.error(f"❌ Erreur OCR avec confiance: {e}")
            return "", 0.0
    
    def extract_from_regions(self, image, regions):
        """Extrait le texte de régions spécifiques"""
        texts = []
        
        for x, y, w, h in regions:
            roi = image[y:y+h, x:x+w]
            text = self.extract_text(roi)
            texts.append(text)
        
        return texts
    
    def correct_common_errors(self, text):
        """Corrige les erreurs OCR communes"""
        corrections = {
            'O': '0',  # O -> 0 dans les chiffres
            'l': '1',  # l -> 1 dans les chiffres
            'S': '5',
            'B': '8',
            'rn': 'm',
            'vv': 'w'
        }
        
        corrected = text
        for wrong, correct in corrections.items():
            # Correction contextuelle (uniquement dans contexte numérique)
            corrected = re.sub(
                r'(?<=\d)' + wrong + r'(?=\d)', 
                correct, 
                corrected
            )
        
        return corrected
    
    def detect_language(self, text):
        """Détecte si le texte est principalement en français"""
        french_words = [
            'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 
            'pour', 'dans', 'avec', 'sur', 'est', 'sont'
        ]
        
        words = text.lower().split()
        french_count = sum(1 for w in words if w in french_words)
        
        ratio = french_count / len(words) if words else 0
        
        return ratio > 0.1  # Au moins 10% de mots français