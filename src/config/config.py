import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Classes de documents
CLASSES = [
    "identite",
    "releve_bancaire", 
    "facture_electricite",
    "facture_eau",
    "document_employeur"
]

# Configuration CV
CV_CONFIG = {
    "model_name": "resnet50",
    "image_size": (224, 224),
    "batch_size": 32,
    "confidence_threshold": 0.8
}

# Configuration NLP
NLP_CONFIG = {
    "ocr_lang": "fra",
    "camembert_model": "camembert-base",
    "max_length": 512,
    "confidence_threshold": 0.8
}

# Configuration Gabarits
TEMPLATE_FEATURES = {
    "identite": {
        "aspect_ratio": (1.5, 1.7),  # Format carte
        "has_photo": True,
        "text_density": (0.3, 0.6)
    },
    "releve_bancaire": {
        "aspect_ratio": (1.3, 1.5),  # Format A4
        "has_table": True,
        "text_density": (0.4, 0.7)
    },
    "facture_electricite": {
        "aspect_ratio": (1.3, 1.5),
        "has_table": True,
        "text_density": (0.3, 0.6)
    },
    "facture_eau": {
        "aspect_ratio": (1.3, 1.5),
        "has_table": True,
        "text_density": (0.3, 0.6)
    },
    "document_employeur": {
        "aspect_ratio": (1.3, 1.5),
        "has_signature": True,
        "text_density": (0.5, 0.8)
    }
}

# Mots-clés par classe
KEYWORDS = {
    "identite": ["identité", "nationale", "cin", "carte", "né(e)", "nationalité", "date"],
    "releve_bancaire": ["solde", "débit", "crédit", "compte", "banque", "opération", "RIB"],
    "facture_electricite": ["kwh", "électricité", "puissance", "abonnement", "consommation", "ONE", "LYDEC"],
    "facture_eau": ["m³", "eau", "consommation", "index", "RADEEMA", "AMENDIS"],
    "document_employeur": ["salaire", "employeur", "embauche", "cotisations", "bulletin", "attestation"]
}

# Configuration Fusion
FUSION_CONFIG = {
    "perfect_agreement_threshold": 0.8,
    "strong_cv_threshold": 0.9,
    "strong_nlp_threshold": 0.9,
    "template_validation_threshold": 0.7,
    "rejection_threshold": 0.6
}