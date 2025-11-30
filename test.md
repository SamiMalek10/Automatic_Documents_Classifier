## 🚀 Installation

### Prérequis

- Python 3.8+
- Tesseract OCR avec support français
- Poppler (pour la conversion PDF → image)
- 4GB RAM minimum
- Connexion internet (uniquement pour le setup initial)

---

### Installation Tesseract (Windows)

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

### Setup du Projet

```bash
# 1. Cloner le repository
git clone <votre-repo>
cd document_classifier

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Lancer le setup offline (avec internet)
python scripts/setup_offline.py
```

Ce script va :
- Installer toutes les dépendances Python (`requirements.txt`)
- Télécharger ResNet50 et CamemBERT
- Créer la structure de dossiers (`data/`, `models/`, etc.)
- Vérifier que Tesseract et Poppler sont accessibles

---

## 💻 Utilisation

### Mode Basique

```bash
# Placer vos PDFs dans data/raw/ (ou utiliser les PDFs factices)
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

---

> ℹ️ **Conseil** : Si tu utilises les PDFs factices, tu peux directement lancer :
> ```bash
> python scripts/fake_pdfs_generator_test.py
> python main.py --input data/raw --output data/output
> ```
