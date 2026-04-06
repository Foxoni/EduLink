import bcrypt # N'oublie pas d'importer bcrypt en haut du fichier

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # On récupère ce que l'utilisateur a tapé
        compte_entre = request.form['username']
        mdp_entre = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. On cherche l'utilisateur uniquement par son NOM DE COMPTE
        # Note : Dans ton seed, la colonne s'appelle 'compte' et non 'username'
        cursor.execute("SELECT * FROM Utilisateurs WHERE compte = %s", (compte_entre,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user:
            # 2. ON VÉRIFIE LE MOT DE PASSE AVEC BCRYPT
            # On compare le mdp tapé avec le mdp crypté de la base (user['mdp'])
            if bcrypt.checkpw(mdp_entre.encode('utf-8'), user['mdp'].encode('utf-8')):
                session['user_id'] = user['id_utilisateur']
                session['prenom'] = user['prenom']
                session['role'] = user['id_role']
                
                # Redirection vers le planning si c'est un élève (id_role = 3)
                if user['id_role'] == 3:
                    return redirect(url_for('mon_planning'))
                return "Connexion réussie (Admin ou Prof)"
            else:
                return "Mot de passe incorrect (Erreur Bcrypt)"
        else:
            return "Compte inexistant"
            
    return render_template('login.html')