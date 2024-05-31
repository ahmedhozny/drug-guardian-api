from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import BaseModel, DrugsModel, DDIModel

load_dotenv()

user = getenv("DB_USER")
passwd = getenv("DB_PASSWD")
db = getenv("DB_NAME")
host = getenv("DB_SERVER")
env = getenv("DB_TEST")

engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                       .format(user, passwd, host, db),
                       pool_pre_ping=True)


# Create all tables
BaseModel.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Sample data
sample_drugs = [
    {
        "drug_ref": "A123456",
        "drug_name": "Paracetamol",
        "brand_name": "Tylenol",
        "indications": "Pain relief",
        "active_ingredient": "Paracetamol",
        "weight": 100.5,
        "smiles": "CC(=O)NC1=CC=CC=C1",
        "drug_bank_ref": 123456
    },
    {
        "drug_ref": "B234567",
        "drug_name": "Ibuprofen",
        "brand_name": "Advil",
        "indications": "Pain relief",
        "active_ingredient": "Ibuprofen",
        "weight": 200.3,
        "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "drug_bank_ref": 654321
    },
    {
        "drug_ref": "C345678",
        "drug_name": "Omeprazole",
        "brand_name": "Prilosec",
        "indications": "Acid reflux treatment",
        "active_ingredient": "Omeprazole",
        "weight": 300.7,
        "smiles": "CC1=CN=C(C(=C1)OC)SCCNC(=O)c2ccccc2",
        "drug_bank_ref": 987654
    },
    {
        "drug_ref": "D456789",
        "drug_name": "Amoxicillin",
        "brand_name": "Amoxil",
        "indications": "Antibiotic",
        "active_ingredient": "Amoxicillin",
        "weight": 150.2,
        "smiles": "CC1(C(N2C(S1)C(C2=O)NC(=O)C(=NOC3=CC=CC=C3)C)O)C",
        "drug_bank_ref": None
    },
    {
        "drug_ref": "E567890",
        "drug_name": "Lisinopril",
        "brand_name": "Zestril",
        "indications": "Hypertension treatment",
        "active_ingredient": "Lisinopril",
        "weight": 175.6,
        "smiles": "CCC(CC)C(=O)N1CCCC1=O",
        "drug_bank_ref": 234567
    },
    {  # New drug - Albuterol
        "drug_ref": "F678901",
        "drug_name": "Albuterol",
        "brand_name": "Proventil",
        "indications": "Asthma treatment",
        "active_ingredient": "Albuterol",
        "weight": 220.8,
        "smiles": "OC(C)=CC1=C(N)C(=C1)C",
        "drug_bank_ref": 345678
    },
    {  # New drug - Fluoxetine
        "drug_ref": "G789012",
        "drug_name": "Fluoxetine",
        "brand_name": "Prozac",
        "indications": "Depression treatment",
        "active_ingredient": "Fluoxetine",
        "weight": 309.3,
        "smiles": "FCCN1C2=C(F)C=CC2=NC1C",
        "drug_bank_ref": 567890
    },
    {
        "drug_ref": "H890123",
        "drug_name": "Atorvastatin",
        "brand_name": "Lipitor",
        "indications": "Cholesterol management",
        "active_ingredient": "Atorvastatin",
        "weight": 320.1,
        "smiles": "CC(C)c1c(C(=O)Nc2ccccc2)nc(N(C)C)n1CC(C)C",
        "drug_bank_ref": 678901
    },
    {
        "drug_ref": "I901234",
        "drug_name": "Metformin",
        "brand_name": "Glucophage",
        "indications": "Diabetes management",
        "active_ingredient": "Metformin",
        "weight": 165.6,
        "smiles": "CN(C)CCCN1C(=O)N(C)C(=O)c2nc3ccccc3[nH]c12",
        "drug_bank_ref": 789012
    },
    {
        "drug_ref": "J012345",
        "drug_name": "Amlodipine",
        "brand_name": "Norvasc",
        "indications": "Hypertension treatment",
        "active_ingredient": "Amlodipine",
        "weight": 411.1,
        "smiles": "CC(C)NCC(O)c1ccccc1C2=NC(=O)OC2=O",
        "drug_bank_ref": 890123
    }
]

# Insert sample data
for drug_data in sample_drugs:
    drug = DrugsModel(**drug_data)
    session.add(drug)

session.commit()

# Sample drug-drug interactions data
interactions_data = [
    {"drug_id_1": 1, "drug_id_2": 2, "interaction": 1},
    {"drug_id_1": 1, "drug_id_2": 3, "interaction": 0},
    {"drug_id_1": 2, "drug_id_2": 4, "interaction": 1}
]

# Insert sample drug-drug interactions into the database
for interaction_data in interactions_data:
    interaction = DDIModel(**interaction_data)
    session.add(interaction)

# Commit changes
session.commit()

# Close session
session.close()
