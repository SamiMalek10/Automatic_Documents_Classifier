from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import logging

class PDFProcessor:
    """Conversion et prétraitement des PDFs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def pdf_to_images(self, pdf_path, dpi=300):
        """Convertit un PDF en liste d'images"""
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            self.logger.info(f"✅ PDF converti: {len(images)} page(s)")
            return [np.array(img) for img in images]
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion PDF: {e}")
            return []
    
    def enhance_image(self, image):
        """Améliore la qualité de l'image pour l'OCR"""
        # Conversion en niveaux de gris
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Débruitage
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Amélioration du contraste (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def correct_skew(self, image):
        """Corrige l'inclinaison de l'image"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotation
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC, 
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def preprocess_for_ocr(self, image):
        """Pipeline complet de prétraitement pour OCR"""
        enhanced = self.enhance_image(image)
        corrected = self.correct_skew(enhanced)
        return corrected
    
    def preprocess_for_cv(self, image, target_size=(224, 224)):
        """Prétraitement pour le modèle CV"""
        # Redimensionnement
        resized = cv2.resize(image, target_size)
        
        # Normalisation ImageNet
        normalized = resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        
        if len(normalized.shape) == 2:
            normalized = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
        
        normalized = (normalized - mean) / std
        
        # Transpose pour PyTorch (H, W, C) -> (C, H, W)
        normalized = np.transpose(normalized, (2, 0, 1))
        
        return normalized