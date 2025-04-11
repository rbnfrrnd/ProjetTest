import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from database import list_users, verify, delete_user_from_db, add_user
from database import read_note_from_db, write_note_into_db
from database import delete_note_from_db, match_user_id_with_note_id
from database import image_upload_record, list_images_for_user
from database import match_user_id_with_image_uid, delete_image_from_db
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config')

@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413

@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")

@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        notes_table = zip([x[0] for x in notes_list],
                          [x[1] for x in notes_list],
                          [x[2] for x in notes_list],
                          ["/delete_note/" + x[0] for x in notes_list])

        images_list = list_images_for_user(session['current_user'])
        images_table = zip([x[0] for x in images_list],
                           [x[1] for x in images_list],
                           [x[2] for x in images_list],
                           ["/delete_image/" + x[0] for x in images_list])

        return render_template("private_page.html", notes=notes_table, images=images_table)
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    if session.get("current_user", None) == "ADMIN":
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),
                         user_list,
                         [x + y for x, y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users=user_table)
    else:
        return abort(401)

@app.route("/write_note", methods=["POST"])
def FUN_write_note():
    text_to_write = request.form.get("text_note_to_take")
    current_user = session.get('current_user', 'Inconnu')
    print(f"[WRITE NOTE] {current_user} a écrit une note : {text_to_write}")
    write_note_into_db(current_user, text_to_write)
    return redirect(url_for("FUN_private"))

@app.route("/delete_note/<note_id>", methods=["GET"])
def FUN_delete_note(note_id):
    current_user = session.get("current_user", None)
    owner = match_user_id_with_note_id(note_id)
    if current_user == owner:
        print(f"[DELETE NOTE] {current_user} a supprimé la note {note_id}")
        delete_note_from_db(note_id)
    else:
        print(f"[DELETE NOTE ÉCHOUÉ] {current_user}"
              " a tenté de supprimer la note {note_id} appartenant à {owner}")
        return abort(401)
    return redirect(url_for("FUN_private"))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_image", methods=['POST'])
def FUN_upload_image():
    if 'file' not in request.files:
        print("[UPLOAD IMAGE] Aucun fichier reçu")
        flash('No file part', category='danger')
        return redirect(url_for("FUN_private"))
    file = request.files['file']
    if file.filename == '':
        print("[UPLOAD IMAGE] Aucun fichier sélectionné")
        flash('No selected file', category='danger')
        return redirect(url_for("FUN_private"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_time = str(datetime.datetime.now())
        image_uid = hashlib.sha256((upload_time + filename).encode()).hexdigest()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_uid + "-" + filename))
        image_upload_record(image_uid, session['current_user'], filename, upload_time)
        print(f"[UPLOAD IMAGE] {session['current_user']} a téléversé : {filename} (UID: {image_uid})")
    return redirect(url_for("FUN_private"))

@app.route("/delete_image/<image_uid>", methods=["GET"])
def FUN_delete_image(image_uid):
    current_user = session.get("current_user", None)
    owner = match_user_id_with_image_uid(image_uid)
    if current_user == owner:
        delete_image_from_db(image_uid)
        image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])]
                                     if y.split("-", 1)[0] == image_uid][0]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        print(f"[DELETE IMAGE] {current_user} a supprimé l'image UID: {image_uid}")
    else:
        print(f"[DELETE IMAGE ÉCHOUÉ] {current_user}"
              " a tenté de supprimer une image appartenant à {owner}")
        return abort(401)
    return redirect(url_for("FUN_private"))

@app.route("/login", methods=["POST"])
def FUN_login():
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
        print(f"[LOGIN] Utilisateur connecté : {id_submitted}")
    else:
        print(f"[LOGIN ÉCHOUÉ] Tentative de connexion pour : {id_submitted}")
    return redirect(url_for("FUN_root"))

@app.route("/logout/")
def FUN_logout():
    user = session.get("current_user", "Inconnu")
    print(f"[LOGOUT] Déconnexion de l'utilisateur : {user}")
    session.pop("current_user", None)
    return redirect(url_for("FUN_root"))

@app.route("/delete_user/<id>/", methods=['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN":
            print("[DELETE USER BLOQUÉ] Tentative de suppression de l’admin")
            return abort(403)
        images_to_remove = [x[0] for x in list_images_for_user(id)]
        for f in images_to_remove:
            image_to_delete_from_pool = [y for y in
                [x for x in os.listdir(app.config['UPLOAD_FOLDER'])]
                if y.split("-", 1)[0] == f][0]
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        delete_user_from_db(id)
        print(f"[DELETE USER] Utilisateur supprimé : {id}")
        return redirect(url_for("FUN_admin"))
    else:
        print("[DELETE USER ÉCHOUÉ] Accès refusé")
        return abort(401)

@app.route("/add_user", methods=["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN":
        user_id = request.form.get('id').upper()
        if user_id in list_users():
            print(f"[ADD USER ÉCHOUÉ] Utilisateur déjà existant : {user_id}")
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),
                             user_list,
                             [x + y for x, y in zip(["/delete_user/"] * len(user_list), user_list)])
            return render_template("admin.html", id_to_add_is_duplicated=True, users=user_table)
        if " " in user_id or "'" in user_id:
            print(f"[ADD USER ÉCHOUÉ] ID invalide : {user_id}")
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),
                             user_list,
                             [x + y for x, y in zip(["/delete_user/"] * len(user_list), user_list)])
            return render_template("admin.html", id_to_add_is_invalid=True, users=user_table)
        else:
            add_user(user_id, request.form.get('pw'))
            print(f"[ADD USER] Nouvel utilisateur ajouté : {user_id}")
            return redirect(url_for("FUN_admin"))
    else:
        print("[ADD USER ÉCHOUÉ] Accès non autorisé à l'ajout utilisateur")
        return abort(401)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="127.0.0.1")
