import mysql.connector
import hashlib
import datetime

# Configuration de la connexion MySQL
DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Remplace par ton utilisateur MySQL
    "password": "",  # Remplace par ton mot de passe MySQL
    "database": "projettest"  # Remplace par le nom de ta base de données
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users;")
    result = [x[0] for x in cursor.fetchall()]
    conn.close()
    return result

def verify(user_id, pw):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pw FROM users WHERE id = %s;", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == hashlib.sha256(pw.encode()).hexdigest()

def delete_user_from_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
    cursor.execute("DELETE FROM notes WHERE user = %s;", (user_id,))
    cursor.execute("DELETE FROM images WHERE owner = %s;", (user_id,))
    conn.commit()
    conn.close()

def add_user(user_id, pw):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (id, pw) VALUES (%s, %s)", (user_id.upper(), 
                hashlib.sha256(pw.encode()).hexdigest()))
    conn.commit()
    conn.close()

def read_note_from_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note_id, timestamp, note FROM notes WHERE user = %s;", 
        (user_id.upper(),))
    result = cursor.fetchall()
    conn.close()
    return result

def match_user_id_with_note_id(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user FROM notes WHERE note_id = %s;", (note_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def write_note_into_db(user_id, note_to_write):
    conn = get_connection()
    cursor = conn.cursor()
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    note_hash = hashlib.sha256((user_id.upper() + current_timestamp).encode()).hexdigest()
    cursor.execute("INSERT INTO notes (user, timestamp, note, note_id) VALUES (%s, %s, %s, %s)", 
                   (user_id.upper(), current_timestamp, note_to_write, note_hash))
    conn.commit()
    conn.close()

def delete_note_from_db(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE note_id = %s;", (note_id,))
    conn.commit()
    conn.close()

def image_upload_record(uid, owner, image_name, timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images (uid, owner, name, timestamp) VALUES (%s, %s, %s, %s)", 
                   (uid, owner, image_name, timestamp))
    conn.commit()
    conn.close()

def list_images_for_user(owner):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, timestamp, name FROM images WHERE owner = %s;", (owner,))
    result = cursor.fetchall()
    conn.close()
    return result

def match_user_id_with_image_uid(image_uid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT owner FROM images WHERE uid = %s;", (image_uid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_image_from_db(image_uid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM images WHERE uid = %s;", (image_uid,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print(list_users())