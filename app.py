from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'une_cle_secrete_tres_sure'

# Configuration de la connexion MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'edulink')
    )

@app.route('/')
def index():
    # Si l'utilisateur n'est pas connecté, on l'envoie vers le login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', prenom=session.get('prenom'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Ici on vérifie dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, prenom FROM utilisateurs WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['prenom'] = user[1]
            return redirect(url_for('index'))
        else:
            return "Identifiants incorrects !"
            
    return render_template('login.html') # Crée ce fichier ou utilise ton fond blanc actuel

@app.route('/mes-notes')
def mes_notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # On récupère les notes de l'élève connecté
    cursor.execute("SELECT valeur, commentaire FROM notes WHERE eleve_id = %s", (session['user_id'],))
    notes_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('eleve/notes.html', prenom=session['prenom'], notes=notes_data)

@app.route('/mon-planning')
def mon_planning():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # On récupère l'emploi du temps
    cursor.execute("SELECT jour, heure_debut, heure_fin, matiere, salle FROM planning ORDER BY FIELD(jour, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')")
    planning_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('eleve/Planning.html', prenom=session['prenom'], planning=planning_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)