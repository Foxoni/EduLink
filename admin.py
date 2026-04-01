from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "devsecops_key"

def get_db_connection():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="root_password",
        database="EduLink" # Correspond au 'USE EduLink' de init.sql
    )

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
    sort_by = request.args.get('sort', 'nom')
    allowed_sorts = ['nom', 'prenom', 'compte', 'nom_role']
    if sort_by not in allowed_sorts:
        sort_by = 'nom'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Requête avec jointures selon le schéma de init.sql
    query = f"""
        SELECT u.id_user, u.nom, u.prenom, u.compte, r.nom_role, c.nom_classe, u.id_classe
        FROM Utilisateurs u
        JOIN Roles r ON u.id_role = r.id_role
        LEFT JOIN Classes c ON u.id_classe = c.id_classe
        ORDER BY {sort_by}
    """
    cursor.execute(query)
    users = cursor.fetchall()
    
    cursor.execute("SELECT id_classe, nom_classe FROM Classes")
    classes = cursor.fetchall()
    conn.close()
    # Chemin mis à jour pour pointer vers templates/admin/utilisateur.html
    return render_template('admin/utilisateur.html', users=users, classes=classes)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
