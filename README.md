# 🗂️ Classification Automatique de Documents Administratifs

Système intelligent de classification offline utilisant Computer Vision et NLP pour trier automatiquement 5 types de documents administratifs marocains.

## 📋 Documents Supportés

1. **Pièce d'identité** (CNIE Recto/Verso)
2. **Relevé bancaire** (toutes banques)
3. **Facture d'électricité** (ONE, LYDEC, RADEEMA, etc.)
4. **Facture d'eau** (AMENDIS, REDAL, etc.)
5. **Document employeur** (bulletins de paie, attestations)

## 🏗️ Architecture

### Pipeline Multimodal

```
PDF → Images → [CV Module] + [NLP Module] → Fusion → Classification
                    ↓              ↓
              Gabarits         Patterns
              ResNet50         Tesseract
                              CamemBERT
```

### Modules Principaux

- **Module CV**: ResNet50 + détection de gabarits structurels
- **Module NLP**: OCR Tesseract + pattern matching + CamemBERT
- **Fusion**: Système expert combinant CV et NLP avec règles métier

## 🚀 Installation

### Prérequis

- Python 3.8+
- Tesseract OCR avec support français
- 4GB RAM minimum
- Connexion internet (uniquement pour le setup initial)

### Installation Tesseract

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra
```

**macOS:**

```bash
brew install tesseract tesseract-lang
```

**Windows:**
1. **Télécharge Tesseract** depuis :  
   👉 [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)  
   → Pendant l’installation, **coche la langue `French (fra)`** si proposée.

2. **Vérifie que le modèle français est présent** :  
   Va dans :  
   ```
   C:\Program Files\Tesseract-OCR\tessdata\
   ```  
   Assure-toi que le fichier **`fra.traineddata`** existe.

   ❌ **S’il manque**, télécharge-le ici :  
   👉 [https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata](https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata)  
   → Enregistre-le directement dans le dossier `tessdata`.

3. **Ajoute Tesseract au PATH** :  
   - Ouvre **Variables d’environnement** (`sysdm.cpl` → "Variables d’environnement")
   - Dans **Variables système**, édite `Path`
   - Ajoute :  
     ```
     C:\Program Files\Tesseract-OCR
     ```
   - Redémarre ton terminal.

---

### Installation Poppler (Windows)

1. **Télécharge Poppler** depuis :  
   👉 [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)  
   (ex: `poppler-25.07.0_x64.7z`)

2. **Décompresse** le fichier, par exemple dans :  
   ```
   C:\poppler-25.07.0_x64\
   ```

3. **Ajoute le dossier `bin` au PATH** :  
   Ajoute cette ligne dans les **Variables d’environnement → Path** :
   ```
   C:\poppler-25.07.0_x64\Library\bin
   ```
   → Redémarre ton terminal.

4. **Vérifie** avec :
   ```powershell
   pdfinfo -v
   ```

---

### Setup du Projet

```bash
# 1. Cloner le repository
git clone <votre-repo>
cd document_classifier

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Lancer le setup offline (avec internet)
python scripts/setup_offline.py
```

Ce script va:

- Installer toutes les dépendances Python
- Télécharger ResNet50 et CamemBERT
- Créer la structure de dossiers
- Vérifier l'environnement


### Génération de PDFs factices (pour tester)

Un script est fourni pour générer **10 PDFs par classe** (50 au total) avec des templates logiques :

```bash
python scripts/fake_pdfs_generator_test.py
```

Cela créera une structure dans `data/raw/` :
```
data/raw/
├── identity_card/
├── bank_statement/
├── electricity_bill/
├── water_bill/
└── employer_doc/
```

> ✅ Idéal pour tester la pipeline sans documents réels.

---

## 💻 Utilisation

### Mode Basique

```bash
# Placer vos PDFs dans data/raw/
# Puis lancer la classification: 
python main.py --input data/raw --output data/output
```

### Options Avancées

```bash
python main.py \
  --input /chemin/vers/pdfs \
  --output /chemin/sortie \
  --models /chemin/modeles
```

### Résultats

Les documents classés seront dans:

```
data/output/
├── identite/
├── releve_bancaire/
├── facture_electricite/
├── facture_eau/
├── document_employeur/
├── a_verifier/          # Documents ambigus
└── classification_report.json
```
---

> ℹ️ **Conseil** : Si tu utilises les PDFs factices, tu peux directement lancer :
> ```bash
> python scripts/fake_pdfs_generator_test.py
> python main.py --input data/raw --output data/output
> ```


## 📊 Métriques et Performances

### Objectifs

- Accuracy par classe: **> 90%**
- Temps moyen: **< 5s par document**
- Taux de rejet: **< 10%**

### Rapport de Classification

Le fichier `classification_report.json` contient:

- Classe prédite et confiance
- Scores CV et NLP individuels
- Chemin de décision (fusion)
- Temps de traitement
- Features extraites

## 🔧 Configuration

Modifier `src/config/config.py` pour ajuster:

```python
# Seuils de confiance
FUSION_CONFIG = {
    'perfect_agreement_threshold': 0.8,
    'strong_cv_threshold': 0.9,
    'rejection_threshold': 0.6
}

# Mots-clés par classe
KEYWORDS = {
    'identite': [...],
    'releve_bancaire': [...]
}
```

## 🧪 Tests

```bash
# Lancer les tests
pytest tests/

# Avec couverture
pytest --cov=src tests/
```

## 📁 Structure du Projet

```
document_classifier/
├── models/              # Modèles sauvegardés (offline)
├── data/
│   ├── raw/            # PDFs d'entrée
│   └── output/         # Documents classés
├── src/
│   ├── config/         # Configuration
│   ├── preprocessing/  # PDF et images
│   ├── cv_module/      # Computer Vision
│   ├── nlp_module/     # NLP et OCR
│   ├── fusion/         # Fusion multimodale
│   └── utils/          # Utilitaires
├── scripts/
│   ├── setup_offline.py
│   └── train_models.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## 🛠️ Développement

### TODO - Améliorations Futures

- [ ] Fine-tuning ResNet50 sur dataset spécifique
- [ ] Entraînement CamemBERT sur corpus administratif
- [ ] Interface web Streamlit
- [ ] Support GPU pour accélération
- [ ] Modèles légers (MobileNet, DistilBERT)
- [ ] Support multi-langues
- [ ] API REST

### Benchmarking

Comparer les performances des modèles:

```bash
python scripts/benchmark_models.py
```

## 👥 Équipe

- **Responsable**: **Zaynab ER-RGHA**Y
- **Membre 1**: **Sami Malek**
- **Membre 2**: **Bilal Lahfari**

## 📄 Licence

Projet académique - INDIA S5 - Pr. CHEFIRA

## 🆘 Support

En cas de problème:

1. Vérifier les logs dans `logs/`
2. Consulter la documentation
3. Ouvrir une issue sur Git

---

**Note**: Ce système fonctionne 100% offline après le setup initial.

