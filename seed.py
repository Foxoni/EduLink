"""
Script de seed pour la base de données EduLink.
Crée les rôles, classes, 1 admin, 6 profs et 9 élèves (3 par classe).
Génère également un fichier credentials.txt récapitulatif.

Usage :
    pip install -r requirements.txt
    python seed.py
"""

import os
import bcrypt
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_FILE = "credentials.txt"

# ── Connexion ────────────────────────────────────────────────────────────────

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
)
cur = conn.cursor()


def hash_mdp(mdp: str) -> str:
    return bcrypt.hashpw(mdp.encode(), bcrypt.gensalt()).decode()


# ── 1. Nettoyage ──────────────────────────────────────────────────────────────

cur.execute("DELETE FROM Notes")
cur.execute("DELETE FROM Evaluation")
cur.execute("DELETE FROM Emploi_du_temps")
cur.execute("DELETE FROM Prof_Classe")
cur.execute("DELETE FROM Utilisateurs")
cur.execute("DELETE FROM Classes")
cur.execute("DELETE FROM Roles")
cur.execute("ALTER TABLE Roles AUTO_INCREMENT = 1")
cur.execute("ALTER TABLE Classes AUTO_INCREMENT = 1")
cur.execute("ALTER TABLE Utilisateurs AUTO_INCREMENT = 1")

# ── 2. Rôles ──────────────────────────────────────────────────────────────────

roles = [
    (1, "Admin"),
    (2, "Professeur"),
    (3, "Eleve"),
]
cur.executemany(
    "INSERT INTO Roles (id_role, nom_role) VALUES (%s, %s)",
    roles,
)
print("✓ Rôles insérés")

# ── 3. Classes ────────────────────────────────────────────────────────────────
# Trois niveaux typiques d'un lycée général

classes = [
    (1, "2nde A"),
    (2, "1ère B"),
    (3, "Tle C"),
]
cur.executemany(
    "INSERT INTO Classes (id_classe, nom_classe) VALUES (%s, %s)",
    classes,
)
print("✓ Classes insérées")

# ── 4. Admin ──────────────────────────────────────────────────────────────────

ADMIN_COMPTE = "admin"
ADMIN_MDP    = "Admin1234!"

cur.execute(
    """
    INSERT INTO Utilisateurs
        (id_role, compte, mdp, nom, prenom, matiere, id_classe)
    VALUES (%s, %s, %s, %s, %s, NULL, NULL)
    """,
    (1, ADMIN_COMPTE, hash_mdp(ADMIN_MDP), "Directeur", "Michel"),
)
print(f"✓ Admin inséré  (compte: {ADMIN_COMPTE} / mdp: {ADMIN_MDP})")

# ── 5. Professeurs ────────────────────────────────────────────────────────────

PROF_MDP = "Prof1234!"

profs = [
    ("prof.martin",   "Martin",   "Sophie",    "Mathématiques"),
    ("prof.dubois",   "Dubois",   "Pierre",    "Français"),
    ("prof.bernard",  "Bernard",  "Claire",    "Histoire-Géographie"),
    ("prof.thomas",   "Thomas",   "Julien",    "Physique-Chimie"),
    ("prof.moreau",   "Moreau",   "Isabelle",  "Sciences de la Vie et de la Terre"),
    ("prof.lefevre",  "Lefèvre",  "Antoine",   "Anglais"),
]

prof_ids = []
for compte, nom, prenom, matiere in profs:
    cur.execute(
        """
        INSERT INTO Utilisateurs
            (id_role, compte, mdp, nom, prenom, matiere, id_classe)
        VALUES (%s, %s, %s, %s, %s, %s, NULL)
        """,
        (2, compte, hash_mdp(PROF_MDP), nom, prenom, matiere),
    )
    prof_ids.append(cur.lastrowid)

print(f"✓ {len(profs)} professeurs insérés  (mdp commun: {PROF_MDP})")

# ── 6. Élèves ─────────────────────────────────────────────────────────────────

ELEVE_MDP = "Eleve1234!"

eleves = [
    # Classe 2nde A (id=1)
    ("eleve.lucas",    "Petit",     "Lucas",    1),
    ("eleve.camille",  "Roux",      "Camille",  1),
    ("eleve.noah",     "Garnier",   "Noah",     1),
    # Classe 1ère B (id=2)
    ("eleve.lea",      "Morel",     "Léa",      2),
    ("eleve.maxime",   "Fontaine",  "Maxime",   2),
    ("eleve.inès",     "Benali",    "Inès",     2),
    # Classe Tle C (id=3)
    ("eleve.hugo",     "Lemaire",   "Hugo",     3),
    ("eleve.manon",    "Girard",    "Manon",    3),
    ("eleve.theo",     "Blanchard", "Théo",     3),
]

for compte, nom, prenom, id_classe in eleves:
    cur.execute(
        """
        INSERT INTO Utilisateurs
            (id_role, compte, mdp, nom, prenom, matiere, id_classe)
        VALUES (%s, %s, %s, %s, %s, NULL, %s)
        """,
        (3, compte, hash_mdp(ELEVE_MDP), nom, prenom, id_classe),
    )

print(f"✓ {len(eleves)} élèves insérés  (mdp commun: {ELEVE_MDP})")

# ── 7. Liaison Prof <-> Classe ────────────────────────────────────────────────
# Chaque prof enseigne dans 2 classes (rotation sur les 3 classes)

prof_classe_liens = [
    (prof_ids[0], 1), (prof_ids[0], 2),   # Martin  (Maths)    → 2nde A, 1ère B
    (prof_ids[1], 1), (prof_ids[1], 3),   # Dubois  (Français) → 2nde A, Tle C
    (prof_ids[2], 2), (prof_ids[2], 3),   # Bernard (Hist-Géo) → 1ère B, Tle C
    (prof_ids[3], 1), (prof_ids[3], 2),   # Thomas  (Phy-Chi)  → 2nde A, 1ère B
    (prof_ids[4], 2), (prof_ids[4], 3),   # Moreau  (SVT)      → 1ère B, Tle C
    (prof_ids[5], 1), (prof_ids[5], 3),   # Lefèvre (Anglais)  → 2nde A, Tle C
]

cur.executemany(
    "INSERT INTO Prof_Classe (id_prof, id_classe) VALUES (%s, %s)",
    prof_classe_liens,
)
print(f"✓ {len(prof_classe_liens)} liens Prof-Classe insérés")

# ── Fin DB ────────────────────────────────────────────────────────────────────

conn.commit()
cur.close()
conn.close()

# ── 8. Génération de credentials.txt ──────────────────────────────────────────

if os.path.exists(CREDENTIALS_FILE):
    os.remove(CREDENTIALS_FILE)

lines = []
lines.append("=" * 60)
lines.append("  EDULINK — CREDENTIALS DE TEST")
lines.append("=" * 60)

lines.append("")
lines.append("── CLASSES ──────────────────────────────────────────────────")
for id_c, nom_c in classes:
    lines.append(f"  [{id_c}] {nom_c}")

lines.append("")
lines.append("── MATIÈRES (par professeur) ─────────────────────────────────")
for compte, nom, prenom, matiere in profs:
    lines.append(f"  {matiere}")

lines.append("")
lines.append("── COMPTE ADMIN ──────────────────────────────────────────────")
lines.append(f"  Compte  : {ADMIN_COMPTE}")
lines.append(f"  Mdp     : {ADMIN_MDP}")
lines.append(f"  Nom     : Michel Directeur")

lines.append("")
lines.append("── COMPTES PROFESSEURS  (mdp commun : Prof1234!) ─────────────")
lines.append(f"  {'Compte':<22} {'Nom':<12} {'Prénom':<12} Matière")
lines.append(f"  {'-'*22} {'-'*12} {'-'*12} {'-'*36}")
for compte, nom, prenom, matiere in profs:
    lines.append(f"  {compte:<22} {nom:<12} {prenom:<12} {matiere}")

lines.append("")
lines.append("── COMPTES ÉLÈVES  (mdp commun : Eleve1234!) ────────────────")
lines.append(f"  {'Compte':<22} {'Nom':<12} {'Prénom':<12} Classe")
lines.append(f"  {'-'*22} {'-'*12} {'-'*12} {'-'*10}")
for compte, nom, prenom, id_classe in eleves:
    nom_classe = next(n for i, n in classes if i == id_classe)
    lines.append(f"  {compte:<22} {nom:<12} {prenom:<12} {nom_classe}")

lines.append("")
lines.append("── AFFECTATIONS PROF → CLASSES ──────────────────────────────")
for i, (compte, nom, prenom, matiere) in enumerate(profs):
    classes_du_prof = [
        next(n for ci, n in classes if ci == id_c)
        for pid, id_c in prof_classe_liens
        if pid == prof_ids[i]
    ]
    lines.append(f"  {prenom} {nom} ({matiere}) → {', '.join(classes_du_prof)}")

lines.append("")
lines.append("=" * 60)
lines.append("  Fichier regénéré à chaque exécution de seed.py")
lines.append("=" * 60)

with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\n✓ Fichier '{CREDENTIALS_FILE}' généré")
print("\n=== Seed terminé avec succès ! ===")
