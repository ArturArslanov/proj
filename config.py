import hashlib

bd_path = 'db/bd.sqlite'
TOKEN = '5139468509:AAGB_IOi22_7ibNP5usNfcI21OYsZaA-6N8'
address = 'http://127.0.0.1:8089/'
secret_key = 'ULTRA_MEGA_SUPER_SECRET_REAl_KEY'

def hashing(text):
    password = text
    salt = hex(15)
    s_password = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return s_password



