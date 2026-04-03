from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "devsecops_key"

def get_db_connection():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="root_password",
        database="EduLink" # Correspond au 'USE EduLink' de init.sql
    )

@app.route('/')
def home():
    return render_template('admin/dashboard.html', nom=None, prenom=None)


@app.route('/logout')
def logout():
    return redirect(url_for('home'))


@app.route('/classes')
def admin_page():
    classes = [] # On initialise une liste vide par sécurité
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # On récupère les classes
        cursor.execute("SELECT id_classe, nom_classe FROM Classes")
        classes = cursor.fetchall()
        conn.close()
    except Exception as e:
        # Si ça plante (ex: table pas encore créée), on affiche l'erreur
        print(f"Erreur de base de données : {e}")
        # En mode debug, on peut aussi flasher l'erreur
        flash(f"Erreur SQL : {e}", "danger")
    
    # Maintenant 'classes' existe forcément (soit remplie, soit vide [])
    return render_template('admin/classe.html', classes=classes)


@app.route('/admin/add-class', methods=['POST'])
def add_class():
    nom = request.form.get('nom_classe')
    if nom:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Utilise bien "Classes" avec une Majuscule
            cursor.execute("INSERT INTO Classes (nom_classe) VALUES (%s)", (nom,))
            conn.commit() # TRÈS IMPORTANT : sans commit, rien n'est sauvé
            conn.close()
            flash(f"Classe '{nom}' ajoutée avec succès !", "success")
        except Exception as e:
            flash(f"Erreur lors de l'ajout : {e}", "danger")
    
    # Redirige vers ta nouvelle route de liste
    return redirect(url_for('admin_page'))

@app.route('/utilisateurs')
def user_page():
    conn = None
    users = []
    roles = []
    classes = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupération des utilisateurs avec le nom de leur rôle et classe
        cursor.execute("""
            SELECT u.*, r.nom_role, c.nom_classe 
            FROM Utilisateurs u
            JOIN Roles r ON u.id_role = r.id_role
            LEFT JOIN Classes c ON u.id_classe = c.id_classe
        """)
        users = cursor.fetchall()
        
        # Récupération des Rôles et Classes pour le formulaire de création
        cursor.execute("SELECT * FROM Roles")
        roles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Classes")
        classes = cursor.fetchall()
        
    except Exception as e:
        flash(f"Erreur SQL : {e}", "danger")
    finally:
        if conn:
            conn.close()
            
    return render_template('admin/utilisateur.html', users=users, roles=roles, classes=classes)

@app.route('/add-user', methods=['POST'])
def add_user():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    compte = request.form.get('compte')
    mdp = request.form.get('mdp')
    id_role = request.form.get('id_role')
    matiere = request.form.get('matiere')
    id_classe = request.form.get('id_classe')

    # Nettoyage : Si le champ est vide, on envoie "None" (NULL) à MySQL
    val_matiere = matiere if matiere and matiere.strip() != "" else None
    val_classe = id_classe if id_classe and id_classe.strip() != "" else None

    conn = None
    try:
        # Hachage du mot de passe
        hashed_mdp = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertion dans la base de données
        cursor.execute("""
            INSERT INTO Utilisateurs (id_role, compte, mdp, nom, prenom, matiere, id_classe)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_role, compte, hashed_mdp, nom, prenom, val_matiere, val_classe))

        conn.commit()
        flash(f"L'utilisateur {prenom} {nom} a été créé avec succès !", "success")
        
    except Exception as e:
        # Si le compte existe déjà (car UNIQUE dans la DB), on intercepte l'erreur
        if "Duplicate entry" in str(e):
            flash("Erreur : Ce compte (pseudo/email) existe déjà.", "danger")
        else:
            flash(f"Erreur lors de la création : {e}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('user_page'))

# ... garder les autres routes (delete_user, update_user_class) telles quelles ...
@app.route('/update-user-class', methods=['POST'])
def update_user_class():
    id_user = request.form.get('id_user')
    id_classe = request.form.get('id_classe')
    conn = get_db_connection()
    cursor = conn.cursor()
    val_classe = id_classe if id_classe and id_classe.strip() != "" else None
    cursor.execute(
        "UPDATE Utilisateurs SET id_classe = %s WHERE id_user = %s", 
        (val_classe, id_user)
    )
    conn.commit()
    conn.close()
    flash("La classe de l'utilisateur a été modifiée avec succès.", "success")
    return redirect(url_for('user_page'))

@app.route('/delete-user/<int:id_user>', methods=['POST'])
def delete_user(id_user):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Utilisateurs WHERE id_user = %s", (id_user,))
        conn.commit()
        flash("Utilisateur supprimé avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {e}", "danger")
    finally:
        conn.close()
    
    # Même chose ici, on redirige vers le nom exact de ta fonction
    return redirect(url_for('user_page'))

@app.route('/emploi-du-temps')
def emploi_page():
    class_id = request.args.get('classe_id')
    conn = None
    classes = []
    emploi = []
    profs = []
    current_classe = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_classe, nom_classe FROM Classes")
        classes = cursor.fetchall()

        if class_id:
            cursor.execute(
                "SELECT id_classe, nom_classe FROM Classes WHERE id_classe = %s",
                (class_id,)
            )
            current_classe = cursor.fetchone()

            cursor.execute("""
                SELECT e.id_cours, e.date, e.heure_debut, e.heure_fin, e.salle,
                       u.nom, u.prenom, u.matiere
                FROM Emploi_du_temps e
                JOIN Utilisateurs u ON e.id_prof = u.id_user
                WHERE e.id_classe = %s
                ORDER BY e.date, e.heure_debut
            """, (class_id,))
            emploi = cursor.fetchall()

            cursor.execute(
                "SELECT id_user, nom, prenom, matiere FROM Utilisateurs WHERE id_role = 2"
            )
            profs = cursor.fetchall()

    except Exception as e:
        flash(f"Erreur SQL : {e}", "danger")
    finally:
        if conn:
            conn.close()

    return render_template('admin/emploi.html', classes=classes, emploi=emploi,
                           current_classe=current_classe, profs=profs)


@app.route('/add-cours', methods=['POST'])
def add_cours():
    id_classe = request.form.get('id_classe')
    id_prof = request.form.get('id_prof')
    date_cours = request.form.get('date')
    salle = request.form.get('salle')
    heure_debut = request.form.get('heure_debut')
    heure_fin = request.form.get('heure_fin')
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # --- VÉRIFICATION DES CONFLITS SUR LA MÊME DATE ---
        # Un conflit existe si le nouveau cours commence avant la fin d'un autre 
        # ET finit après le début de cet autre cours.
        cursor.execute("""
            SELECT id_cours FROM Emploi_du_temps 
            WHERE id_classe = %s AND date = %s 
            AND (heure_debut < %s AND heure_fin > %s)
        """, (id_classe, date_cours, heure_fin, heure_debut))
        
        conflit = cursor.fetchone()
        
        if conflit:
            flash("Action bloquée : La classe a déjà un cours sur ce créneau à cette date !", "danger")
        else:
            # On insère avec tes colonnes exactes
            cursor.execute("""
                INSERT INTO Emploi_du_temps (id_classe, id_prof, salle, date, heure_debut, heure_fin)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_classe, id_prof, salle, date_cours, heure_debut, heure_fin))
            conn.commit()
            flash("Cours ajouté avec succès au planning.", "success")
            
    except Exception as e:
        flash(f"Erreur lors de l'ajout : {e}", "danger")
    finally:
        if conn:
            conn.close()
            
    return redirect(url_for('emploi_page', classe_id=id_classe))

@app.route('/delete-class/<int:id_classe>', methods=['POST'])
def delete_class(id_classe):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Classes WHERE id_classe = %s", (id_classe,))
        conn.commit()
        flash("Classe supprimée avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {e}", "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('admin_page'))


@app.route('/delete-cours/<int:id_cours>', methods=['POST'])
def delete_cours(id_cours):
    classe_id = request.form.get('classe_id')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Emploi_du_temps WHERE id_cours = %s", (id_cours,))
        conn.commit()
        flash("Cours supprimé avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {e}", "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('emploi_page', classe_id=classe_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
