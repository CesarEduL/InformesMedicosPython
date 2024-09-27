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

# Función para verificar el DNI del paciente en Firebase
def verificar_dni_paciente(dni):
    ref = db.reference(f'pacientes/{dni}')
    paciente = ref.get()
    return paciente

# Función para verificar el DNI del administrador en Firebase
def verificar_dni_admin(dni):
    ref = db.reference(f'directivos/{dni}')
    admin = ref.get()
    return admin

# Función para crear un usuario paciente en la Realtime Database
def crear_paciente(dni, nombre):
    ref = db.reference('pacientes')
    paciente_ref = ref.child(dni)
    paciente_ref.set({
        'nombre': nombre,
        'dni': dni
    })

#Funciones admin


def get_all_patients():
    ref = db.reference('pacientes')
    return ref.get()


def get_patient(dni):
    ref = db.reference(f'pacientes/{dni}')
    return ref.get()


def update_patient(dni, nombre):
    ref = db.reference(f'pacientes/{dni}')
    ref.update({'nombre': nombre})


def delete_patient_by_dni(dni):
    ref = db.reference(f'pacientes/{dni}')
    ref.delete()


def get_all_doctors():
    ref = db.reference('medicos')
    return ref.get()


def get_doctor(dni):
    ref = db.reference(f'medicos/{dni}')
    return ref.get()


def crear_medico(dni, nombre, especialidad):
    ref = db.reference('medicos')
    medico_ref = ref.child(dni)
    medico_ref.set({
        'nombre': nombre,
        'dni': dni,
        'especialidad': especialidad
    })


def update_doctor(dni, nombre, especialidad):
    ref = db.reference(f'medicos/{dni}')
    ref.update({'nombre': nombre, 'especialidad': especialidad})


def delete_doctor_by_dni(dni):
    ref = db.reference(f'medicos/{dni}')
    ref.delete()
