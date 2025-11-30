import argparse
import logging
from pathlib import Path
import json
import time
from tqdm import tqdm

from src.utils.offline_manager import OfflineModelManager
from src.preprocessing.pdf_processor import PDFProcessor
from src.cv_module.template_detector import TemplateDetector
from src.nlp_module.ocr_extractor import OCRExtractor
from src.nlp_module.pattern_matcher import PatternMatcher
from src.fusion.multimodal_fusion import MultimodalFusion
from src.config.config import CLASSES, DATA_DIR

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DocumentClassifier:
    """Pipeline principal de classification"""
    
    def __init__(self, models_dir):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des modules
        self.logger.info("🚀 Initialisation du système...")
        
        self.model_manager = OfflineModelManager(models_dir)
        self.pdf_processor = PDFProcessor()
        self.template_detector = TemplateDetector()
        self.ocr_extractor = OCRExtractor()
        self.pattern_matcher = PatternMatcher()
        self.fusion = MultimodalFusion()
        
        self.logger.info("✅ Système initialisé")
    
    def classify_image(self, image):
        """Classifie une seule image"""
        
        # 1. Extraction des features de gabarits
        template_features = self.template_detector.extract_features(image)
        
        # Calcul des scores pour chaque classe
        template_scores = {}
        for cls in CLASSES:
            score = self.template_detector.match_template(template_features, cls)
            template_scores[cls] = score
        
        template_features['template_scores'] = template_scores
        
        # 2. Classification CV (simplifié pour cette version)
        # TODO: Implémenter le modèle ResNet50 hybride
        cv_pred = max(template_scores, key=template_scores.get)
        cv_conf = template_scores[cv_pred]
        
        # 3. Extraction et classification NLP
        # Prétraitement pour OCR
        ocr_image = self.pdf_processor.preprocess_for_ocr(image)
        
        # OCR
        text, ocr_confidence = self.ocr_extractor.extract_with_confidence(ocr_image)
        
        # Pattern matching
        nlp_pred, nlp_conf, pattern_scores = self.pattern_matcher.predict(text)
        
        # Extraction des patterns spécifiques
        text_patterns = self.pattern_matcher.extract_specific_patterns(text)
        
        # Force NLP pred si aucune prédiction
        if nlp_pred is None:
            nlp_pred = cv_pred
            nlp_conf = 0.1
        
        pattern_strength = max(pattern_scores.values()) if pattern_scores else 0.0
        
        # 4. Fusion multimodale
        final_class, final_conf, decision_path, should_reject = self.fusion.fuse(
            cv_result=(cv_pred, cv_conf),
            nlp_result=(nlp_pred, nlp_conf, pattern_strength),
            template_features=template_features,
            text_patterns=text_patterns
        )
        
        return {
            'predicted_class': final_class,
            'confidence': final_conf,
            'decision_path': decision_path,
            'rejected': should_reject,
            'cv_prediction': cv_pred,
            'cv_confidence': cv_conf,
            'nlp_prediction': nlp_pred,
            'nlp_confidence': nlp_conf,
            'ocr_confidence': ocr_confidence,
            'text_length': len(text),
            'template_scores': template_scores,
            'pattern_scores': pattern_scores
        }
    
    def process_pdf(self, pdf_path, output_dir):
        """Traite un PDF complet"""
        
        self.logger.info(f"📄 Traitement: {pdf_path}")
        
        # Conversion PDF -> images
        images = self.pdf_processor.pdf_to_images(pdf_path)
        
        if not images:
            self.logger.error("❌ Impossible de convertir le PDF")
            return []
        
        results = []
        
        for i, image in enumerate(tqdm(images, desc="Pages")):
            self.logger.info(f"  Page {i+1}/{len(images)}")
            
            result = self.classify_image(image)
            result['page_number'] = i + 1
            results.append(result)
            
            # Sauvegarde dans le dossier approprié
            if result['rejected']:
                output_folder = output_dir / "a_verifier"
            else:
                output_folder = output_dir / result['predicted_class']
            
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarde de l'image
            import cv2
            output_path = output_folder / f"{Path(pdf_path).stem}_page{i+1}.jpg"
            cv2.imwrite(str(output_path), image)
        
        return results
    
    def process_batch(self, input_dir, output_dir):
        """Traite un lot de PDFs"""
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
                # Recherche récursive de tous les PDFs dans input_dir et ses sous-dossiers
        pdf_files = list(input_path.rglob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning("⚠️ Aucun PDF trouvé dans le dossier ou ses sous-dossiers")
            return
        
        
        self.logger.info(f"📚 {len(pdf_files)} PDF(s) à traiter")
        #for p in pdf_files:
        #    self.logger.info(f"  - {p}")
        
        all_results = {}
        
        for pdf_file in pdf_files:
            start_time = time.time()
            
            results = self.process_pdf(pdf_file, output_path)
            
            elapsed = time.time() - start_time
            
            all_results[str(pdf_file)] = {
                'results': results,
                'processing_time': elapsed,
                'pages_count': len(results)
            }
            
            self.logger.info(f"✅ Terminé en {elapsed:.2f}s")
        
        # Sauvegarde du rapport global
        report_path = output_path / "classification_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Rapport sauvegardé: {report_path}")
        
        return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Classification automatique de documents administratifs"
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help="Dossier contenant les PDFs à traiter"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/output',
        help="Dossier de sortie pour les documents classés"
    )
    
    parser.add_argument(
        '--models', '-m',
        type=str,
        default='models',
        help="Dossier contenant les modèles"
    )
    
    args = parser.parse_args()
    
    # Création du classifier
    classifier = DocumentClassifier(args.models)
    
    # Traitement
    classifier.process_batch(args.input, args.output)
    
    print("\n✅ Traitement terminé!")


if __name__ == "__main__":
    main()