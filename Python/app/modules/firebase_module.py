import firebase_admin
from firebase_admin import credentials, db, firestore

# Inicializar Firebase con el archivo de credenciales
def inicializar_firebase():
    cred = credentials.Certificate("app/config/firebase_config.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://informesmedicos-aacda-default-rtdb.firebaseio.com/'
    })

# Inicializar Firestore
def obtener_firestore():
    return firestore.client()

# Función para verificar el DNI del médico en Firebase
def verificar_dni_medico(dni):
    ref = db.reference(f'medicos/{dni}')
    medico = ref.get()
    return medico
