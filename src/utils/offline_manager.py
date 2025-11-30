import os
import torch
import torchvision.models as models
from transformers import CamembertModel, CamembertTokenizer
from pathlib import Path
import logging

class OfflineModelManager:
    """Gestionnaire de modèles fonctionnant 100% offline"""
    
    def __init__(self, models_dir):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        self.logger = logging.getLogger(__name__)
        
    def download_and_save_models(self):
        """Télécharge et sauvegarde tous les modèles une seule fois"""
        print("📥 Téléchargement des modèles...")
        
        # 1. Télécharger ResNet50
        cv_path = self.models_dir / "cv"
        cv_path.mkdir(exist_ok=True)
        
        print("  - ResNet50...")
        resnet = models.resnet50(pretrained=True)
        torch.save(resnet.state_dict(), cv_path / "resnet50.pth")
        
        # 2. Télécharger CamemBERT
        nlp_path = self.models_dir / "nlp"
        nlp_path.mkdir(exist_ok=True)
        
        print("  - CamemBERT...")
        tokenizer = CamembertTokenizer.from_pretrained('camembert-base')
        model = CamembertModel.from_pretrained('camembert-base')
        
        tokenizer.save_pretrained(nlp_path / "camembert")
        model.save_pretrained(nlp_path / "camembert")
        
        print("✅ Tous les modèles sont sauvegardés localement")
        
    def load_resnet50(self):
        """Charge ResNet50 depuis le stockage local"""
        if 'resnet50' in self.loaded_models:
            return self.loaded_models['resnet50']
        
        cv_path = self.models_dir / "cv" / "resnet50.pth"
        if not cv_path.exists():
            raise FileNotFoundError(f"Modèle ResNet50 introuvable: {cv_path}")
        
        model = models.resnet50(pretrained=False)
        model.load_state_dict(torch.load(cv_path, map_location='cpu'))
        model.eval()
        
        self.loaded_models['resnet50'] = model
        self.logger.info("✅ ResNet50 chargé depuis le stockage local")
        return model
    
    def load_camembert(self):
        """Charge CamemBERT depuis le stockage local"""
        if 'camembert' in self.loaded_models:
            return self.loaded_models['camembert']
        
        nlp_path = self.models_dir / "nlp" / "camembert"
        if not nlp_path.exists():
            raise FileNotFoundError(f"Modèle CamemBERT introuvable: {nlp_path}")
        
        tokenizer = CamembertTokenizer.from_pretrained(str(nlp_path))
        model = CamembertModel.from_pretrained(str(nlp_path))
        model.eval()
        
        self.loaded_models['camembert'] = {'model': model, 'tokenizer': tokenizer}
        self.logger.info("✅ CamemBERT chargé depuis le stockage local")
        return model, tokenizer
    
    def verify_offline_setup(self):
        """Vérifie que tout fonctionne en mode offline"""
        checks = {
            "ResNet50": (self.models_dir / "cv" / "resnet50.pth").exists(),
            "CamemBERT": (self.models_dir / "nlp" / "camembert").exists(),
        }
        
        all_ok = all(checks.values())
        
        print("\n🔍 Vérification de l'environnement offline:")
        for name, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}")
        
        return all_ok