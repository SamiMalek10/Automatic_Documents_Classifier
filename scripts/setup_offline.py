#!/usr/bin/env python3
"""
Script d'initialisation de l'environnement offline
À exécuter UNE SEULE FOIS avec connexion internet
"""

import os
import sys
from pathlib import Path
import subprocess


ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
def check_tesseract():
    """Vérifie l'installation de Tesseract"""
    print("🔍 Vérification de Tesseract OCR...")
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract est installé")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Tesseract n'est pas installé")
    print("\n📝 Instructions d'installation:")
    print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-fra")
    print("  macOS: brew install tesseract tesseract-lang")
    print("  Windows: Télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def create_directory_structure():
    """Crée la structure de dossiers"""
    print("\n📁 Création de la structure de dossiers...")
    
    dirs = [
        "models/cv",
        "models/nlp",
        "models/fusion",
        "data/raw",
        "data/processed",
        "data/output/identite",
        "data/output/releve_bancaire",
        "data/output/facture_electricite",
        "data/output/facture_eau",
        "data/output/document_employeur",
        "data/output/a_verifier",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")

def install_dependencies():
    """Installe les dépendances Python"""
    print("\n📦 Installation des dépendances Python...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation des dépendances")
        return False

def download_models():
    """Télécharge et sauvegarde les modèles"""
    print("\n🤖 Téléchargement des modèles (cela peut prendre plusieurs minutes)...")
    
    try:

        # Ajoute la racine du projet au chemin Python
        #sys.path.insert(0, str(Path(__file__).parent.resolve()))

        # Maintenant les imports de `src` devraient fonctionner
        from src.utils.offline_manager import OfflineModelManager
        
        manager = OfflineModelManager("models")
        manager.download_and_save_models()
        
        print("✅ Modèles téléchargés et sauvegardés")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def verify_setup():
    """Vérifie que tout est correctement installé"""
    print("\n🔍 Vérification finale...")
    
    try:
        #sys.path.insert(0, str(Path(__file__).parent.resolve()))
        from src.utils.offline_manager import OfflineModelManager
        
        manager = OfflineModelManager("models")
        all_ok = manager.verify_offline_setup()
        
        if all_ok:
            print("\n✅ ✅ ✅ Installation complète! Le système peut maintenant fonctionner offline.")
            return True
        else:
            print("\n⚠️ Certains composants sont manquants")
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 SETUP ENVIRONNEMENT OFFLINE")
    print("   Classification de Documents Administratifs")
    print("=" * 60)
    
    """
    # Étape 1: Vérifier Tesseract
    if not check_tesseract():
       print("\n⚠️ Veuillez installer Tesseract avant de continuer")
       return
    
    # Étape 2: Créer la structure
    create_directory_structure()
    
    # Étape 3: Installer les dépendances
    if not install_dependencies():
        print("\n⚠️ Échec de l'installation des dépendances")
        return
    """
    # Étape 4: Télécharger les modèles
    if not download_models():
        print("\n⚠️ Échec du téléchargement des modèles")
        return
    
    # Étape 5: Vérification finale
    verify_setup()
    
    print("\n" + "=" * 60)
    print("📝 PROCHAINES ÉTAPES:")
    print("  1. Placez vos PDFs dans le dossier data/raw/")
    print("  2. Lancez: python main.py --input data/raw --output data/output")
    print("  3. Les documents classés seront dans data/output/")
    print("=" * 60)

if __name__ == "__main__":
    main()