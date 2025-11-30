import cv2
import numpy as np
from src.config.config import TEMPLATE_FEATURES

class TemplateDetector:
    """Détecteur de features structurelles pour gabarits"""
    
    def __init__(self):
        # Chargement du détecteur de visages pour photos
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def compute_aspect_ratio(self, image):
        """Calcule le ratio hauteur/largeur"""
        h, w = image.shape[:2]
        return h / w if w > 0 else 0
    
    def detect_photo(self, image):
        """Détecte la présence d'une photo"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        return len(faces) > 0, len(faces)
    
    def detect_table_structure(self, image):
        """Détecte une structure tabulaire"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Détection de lignes horizontales
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines_h = cv2.HoughLinesP(
            edges, 1, np.pi/180, 100, 
            minLineLength=100, maxLineGap=10
        )
        
        # Détection de lignes verticales
        lines_v = cv2.HoughLinesP(
            edges, 1, np.pi/2, 100,
            minLineLength=100, maxLineGap=10
        )
        
        h_count = len(lines_h) if lines_h is not None else 0
        v_count = len(lines_v) if lines_v is not None else 0
        
        # Si beaucoup de lignes H et V -> structure tabulaire
        has_table = h_count > 3 and v_count > 3
        
        return has_table, h_count, v_count
    
    def compute_text_density(self, image):
        """Calcule la densité de texte"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Binarisation
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Pourcentage de pixels texte
        text_pixels = np.sum(binary > 0)
        total_pixels = binary.size
        
        density = text_pixels / total_pixels if total_pixels > 0 else 0
        
        return density
    
    def detect_signature_zone(self, image):
        """Détecte les zones potentielles de signature"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Recherche de zones avec texture particulière (signature manuscrite)
        # Utilisation de la variance locale
        kernel_size = 15
        mean = cv2.blur(gray, (kernel_size, kernel_size))
        sqr_mean = cv2.blur(gray**2, (kernel_size, kernel_size))
        variance = sqr_mean - mean**2
        
        # Zones à forte variance = potentiellement manuscrites
        threshold = np.percentile(variance, 95)
        signature_mask = variance > threshold
        
        signature_ratio = np.sum(signature_mask) / signature_mask.size
        
        return signature_ratio > 0.05, signature_ratio
    
    def extract_features(self, image):
        """Extrait toutes les features structurelles"""
        features = {
            'aspect_ratio': self.compute_aspect_ratio(image),
            'has_photo': self.detect_photo(image)[0],
            'photo_count': self.detect_photo(image)[1],
            'has_table': self.detect_table_structure(image)[0],
            'horizontal_lines': self.detect_table_structure(image)[1],
            'vertical_lines': self.detect_table_structure(image)[2],
            'text_density': self.compute_text_density(image),
            'has_signature': self.detect_signature_zone(image)[0],
            'signature_ratio': self.detect_signature_zone(image)[1]
        }
        
        return features
    
    def match_template(self, features, class_name):
        """Calcule le score de correspondance avec un gabarit"""
        if class_name not in TEMPLATE_FEATURES:
            return 0.0
        
        template = TEMPLATE_FEATURES[class_name]
        score = 0.0
        total_weight = 0.0
        
        # Vérification aspect ratio
        if 'aspect_ratio' in template:
            min_r, max_r = template['aspect_ratio']
            if min_r <= features['aspect_ratio'] <= max_r:
                score += 0.3
            total_weight += 0.3
        
        # Vérification photo
        if template.get('has_photo', False):
            if features['has_photo']:
                score += 0.3
            total_weight += 0.3
        
        # Vérification table
        if template.get('has_table', False):
            if features['has_table']:
                score += 0.2
            total_weight += 0.2
        
        # Vérification densité texte
        if 'text_density' in template:
            min_d, max_d = template['text_density']
            if min_d <= features['text_density'] <= max_d:
                score += 0.2
            total_weight += 0.2
        
        return score / total_weight if total_weight > 0 else 0.0