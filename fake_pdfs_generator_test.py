import os
import random
from fpdf import FPDF
from datetime import datetime, timedelta

# --- CONFIGURATION ---
BASE_DIR = "data/raw"
CLASSES = [
    "identity_card",
    "bank_statement",
    "electricity_bill",
    "water_bill",
    "employer_doc"
]

# Textes fictifs par catégorie
TEXTS = {
    "identity_card": [
        "Carte Nationale d'Identité Électronique",
        "Nom : {nom}",
        "Prénom : {prenom}",
        "Date de naissance : {date_naissance}",
        "Lieu de naissance : {lieu}",
        "Numéro de carte : {num_carte}",
        "Date d'émission : {date_emission}",
        "Date d'expiration : {date_expiration}",
        "Signature : _________________________",
        "Cet exemplaire est un document officiel."
    ],
    "bank_statement": [
        "Relevé de compte bancaire",
        "Banque : {banque}",
        "Titulaire : {nom_prenom}",
        "Numéro de compte : {num_compte}",
        "Période : {debut} au {fin}",
        "Solde initial : {solde_debut} MAD",
        "Solde final : {solde_fin} MAD",
        "Opérations :",
        "  - {op1} : +{montant1} MAD",
        "  - {op2} : -{montant2} MAD",
        "  - {op3} : +{montant3} MAD",
        "Frais de gestion : {frais} MAD",
        "Signature du responsable : ______________"
    ],
    "electricity_bill": [
        "Facture d'électricité",
        "Fournisseur : Électricité Maroc",
        "Client : {nom_prenom}",
        "Adresse : {adresse}",
        "Référence client : {ref_client}",
        "Période : {debut} au {fin}",
        "Consommation : {kwh} kWh",
        "Montant à payer : {montant} MAD",
        "Date d'échéance : {echeance}",
        "Mode de paiement : Virement / Guichet",
        "Merci pour votre confiance."
    ],
    "water_bill": [
        "Facture d'eau potable",
        "Fournisseur : ONEE",
        "Client : {nom_prenom}",
        "Adresse : {adresse}",
        "Numéro compteur : {num_compteur}",
        "Période : {debut} au {fin}",
        "Volume consommé : {m3} m³",
        "Montant total : {montant} MAD",
        "Date de paiement : {echeance}",
        "Retard de paiement : pénalités appliquées.",
        "Service client : 0800 000 000"
    ],
    "employer_doc": [
        "Attestation d'emploi",
        "Entreprise : {entreprise}",
        "Employé : {nom_prenom}",
        "Poste : {poste}",
        "Date d'embauche : {embauche}",
        "Salaire mensuel : {salaire} MAD",
        "Statut : {statut}",
        "Cette attestation est délivrée à l'employé pour ses besoins personnels.",
        "Signé par le DRH : _______________",
        "Document valable 3 mois à compter de sa date.",
        "",
        "--- BULLETIN DE PAIE ---",
        "Mois : {mois}",
        "Base salaire : {base} MAD",
        "Heures supplémentaires : {hs} MAD",
        "Déductions : {deductions} MAD",
        "Net à payer : {net} MAD"
    ]
}

# Données aléatoires
NAMES = ["Mohamed", "Fatima", "Ali", "Amina", "Youssef", "Sara", "Karim", "Leila", "Omar", "Nadia"]
BANKS = ["Attijariwafa Bank", "BMCE Bank", "CIH Bank", "Bank of Africa", "Crédit Agricole"]
COMPANIES = ["Société Générale Maroc", "Maroc Telecom", "TotalEnergies Maroc", "SNI", "Groupe OCP"]
ADDRESSES = [
    "Rue des Fleurs, Casablanca",
    "Avenue Mohammed V, Rabat",
    "Quartier Anfa, Casablanca",
    "Hay Riad, Rabat",
    "Marrakech Medina, Marrakech"
]
POSTES = ["Ingénieur Logiciel", "Comptable", "Technicien", "Chef de Projet", "Assistant RH"]

def generate_random_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%d/%m/%Y")

def generate_fake_text(class_name):
    template = random.choice(TEXTS[class_name])
    if class_name == "identity_card":
        nom = random.choice(NAMES)
        prenom = random.choice(NAMES)
        date_naissance = generate_random_date(1970, 2005)
        lieu = random.choice(["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger"])
        num_carte = f"CNIE-{random.randint(1000000, 9999999)}"
        date_emission = generate_random_date(2020, 2024)
        date_expiration = generate_random_date(2025, 2027)
        return template.format(
            nom=nom, prenom=prenom, date_naissance=date_naissance,
            lieu=lieu, num_carte=num_carte, date_emission=date_emission,
            date_expiration=date_expiration
        )
    elif class_name == "bank_statement":
        banque = random.choice(BANKS)
        nom_prenom = f"{random.choice(NAMES)} {random.choice(NAMES)}"
        num_compte = f"MA{random.randint(1000000000, 9999999999)}"
        debut = generate_random_date(2023, 2024)
        fin = generate_random_date(2024, 2025)
        solde_debut = round(random.uniform(500, 5000), 2)
        solde_fin = round(solde_debut + random.uniform(-2000, 2000), 2)
        op1 = random.choice(["Virement", "Retrait", "Dépôt"])
        op2 = random.choice(["Virement", "Retrait", "Dépôt"])
        op3 = random.choice(["Virement", "Retrait", "Dépôt"])
        montant1 = round(random.uniform(100, 2000), 2)
        montant2 = round(random.uniform(50, 1500), 2)
        montant3 = round(random.uniform(200, 3000), 2)
        frais = round(random.uniform(0, 50), 2)
        return template.format(
            banque=banque, nom_prenom=nom_prenom, num_compte=num_compte,
            debut=debut, fin=fin, solde_debut=solde_debut, solde_fin=solde_fin,
            op1=op1, montant1=montant1, op2=op2, montant2=montant2,
            op3=op3, montant3=montant3, frais=frais
        )
    elif class_name == "electricity_bill":
        nom_prenom = f"{random.choice(NAMES)} {random.choice(NAMES)}"
        adresse = random.choice(ADDRESSES)
        ref_client = f"REF-{random.randint(100000, 999999)}"
        debut = generate_random_date(2023, 2024)
        fin = generate_random_date(2024, 2025)
        kwh = random.randint(50, 500)
        montant = round(kwh * 0.8 + random.uniform(50, 200), 2)
        echeance = generate_random_date(2025, 2026)
        return template.format(
            nom_prenom=nom_prenom, adresse=adresse, ref_client=ref_client,
            debut=debut, fin=fin, kwh=kwh, montant=montant, echeance=echeance
        )
    elif class_name == "water_bill":
        nom_prenom = f"{random.choice(NAMES)} {random.choice(NAMES)}"
        adresse = random.choice(ADDRESSES)
        num_compteur = f"WC-{random.randint(100000, 999999)}"
        debut = generate_random_date(2023, 2024)
        fin = generate_random_date(2024, 2025)
        m3 = round(random.uniform(5, 50), 1)
        montant = round(m3 * 5 + random.uniform(10, 100), 2)
        echeance = generate_random_date(2025, 2026)
        return template.format(
            nom_prenom=nom_prenom, adresse=adresse, num_compteur=num_compteur,
            debut=debut, fin=fin, m3=m3, montant=montant, echeance=echeance
        )
    elif class_name == "employer_doc":
        entreprise = random.choice(COMPANIES)
        nom_prenom = f"{random.choice(NAMES)} {random.choice(NAMES)}"
        poste = random.choice(POSTES)
        embauche = generate_random_date(2020, 2024)
        salaire = round(random.uniform(5000, 20000), 2)
        statut = random.choice(["CDI", "CDD", "Stage"])
        mois = random.choice(["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        base = round(salaire * 0.8, 2)
        hs = round(random.uniform(0, 500), 2)
        deductions = round(random.uniform(100, 1000), 2)
        net = round(base + hs - deductions, 2)
        return template.format(
            entreprise=entreprise, nom_prenom=nom_prenom, poste=poste,
            embauche=embauche, salaire=salaire, statut=statut,
            mois=mois, base=base, hs=hs, deductions=deductions, net=net
        )

def create_pdf_for_class(class_name, num_files=10):
    folder_path = os.path.join(BASE_DIR, class_name)
    os.makedirs(folder_path, exist_ok=True)

    for i in range(1, num_files + 1):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Document Factice : {class_name.replace('_', ' ').title()}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        for _ in range(15):  # Ajoute 15 lignes de texte aléatoire
            line = generate_fake_text(class_name)
            pdf.multi_cell(0, 6, line)
            pdf.ln(2)

        filename = f"{class_name}_{i:03d}.pdf"
        filepath = os.path.join(folder_path, filename)
        pdf.output(filepath)
        print(f"✅ Generated: {filepath}")

if __name__ == "__main__":
    print("🚀 Génération de PDF factices en cours...")

    for cls in CLASSES:
        print(f"\n📁 Génération pour : {cls}")
        create_pdf_for_class(cls, num_files=10)  # 10 PDF par classe

    print("\n🎉 Tous les PDF factices ont été générés avec succès !")