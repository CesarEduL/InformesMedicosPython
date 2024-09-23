import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, db, firestore
import requests
import json
from datetime import datetime
import os

# Función para cargar el token desde el archivo config.json
def cargar_token():
    with open('app/config.json', 'r') as file:
        config = json.load(file)
    return config['API_TOKEN']

# Inicializar Firebase con el archivo de credenciales
cred = credentials.Certificate("app/firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://informesmedicos-aacda-default-rtdb.firebaseio.com/'
})

# Inicializar Firestore
db_firestore = firestore.client()

# Cargar el token de la API de la SUNAT
API_TOKEN = cargar_token()

# Función para verificar el DNI del médico en Firebase
def verificar_dni_medico(dni):
    ref = db.reference(f'medicos/{dni}')
    medico = ref.get()
    return medico

# Función para obtener el nombre del paciente usando la API de la RENIEC
def obtener_nombre_paciente(dni):
    url = f"https://api.apis.net.pe/v1/dni?numero={dni}"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'nombres' in data and 'apellidoPaterno' in data and 'apellidoMaterno' in data:
                return f"{data['nombres']} {data['apellidoPaterno']} {data['apellidoMaterno']}"
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return None

# Función para crear un PDF del informe médico
def crear_pdf(dni_paciente, nombre_paciente, informe_texto, diagnostico, tratamiento, nombre_medico):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe Médico", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.cell(0, 10, txt="", ln=True)

    pdf.cell(0, 10, txt=f"DNI del Paciente: {dni_paciente}", ln=True)
    pdf.cell(0, 10, txt=f"Nombre del Paciente: {nombre_paciente}", ln=True)
    pdf.cell(0, 10, txt=f"Diagnóstico: {diagnostico}", ln=True)
    pdf.cell(0, 10, txt=f"Tratamiento: {tratamiento}", ln=True)
    pdf.cell(0, 10, txt=f"Médico: {nombre_medico}", ln=True)  # Nombre del médico
    pdf.cell(0, 10, txt="", ln=True)
    pdf.multi_cell(0, 10, txt=f"Informe:\n{informe_texto}")

    # Guardar el PDF en la carpeta de Descargas
    downloads_path = os.path.expanduser("~/Downloads")
    pdf_file_name = os.path.join(downloads_path, f"Informe_Medico_{dni_paciente}.pdf")
    pdf.output(pdf_file_name)
    return pdf_file_name

# Función para abrir la ventana de informe médico
def abrir_informe_medico(nombre_medico):
    informe_ventana = tk.Toplevel(root)
    informe_ventana.title("Informe Médico")
    informe_ventana.geometry("600x400")

    tk.Label(informe_ventana, text="DNI del Paciente:").pack()
    dni_paciente_entry = tk.Entry(informe_ventana)
    dni_paciente_entry.pack()

    tk.Label(informe_ventana, text="Nombre del Paciente:").pack()
    nombre_paciente_entry = tk.Entry(informe_ventana)
    nombre_paciente_entry.pack()

    def autocompletar_nombre():
        dni_paciente = dni_paciente_entry.get()
        nombre_paciente = obtener_nombre_paciente(dni_paciente)
        if nombre_paciente:
            nombre_paciente_entry.delete(0, tk.END)
            nombre_paciente_entry.insert(0, nombre_paciente)
        else:
            messagebox.showerror("Error", "No se pudo autocompletar el nombre o DNI no encontrado")

    tk.Button(informe_ventana, text="Autocompletar Nombre", command=autocompletar_nombre).pack()

    tk.Label(informe_ventana, text="Diagnóstico:").pack()
    diagnostico_entry = tk.Entry(informe_ventana)
    diagnostico_entry.pack()

    tk.Label(informe_ventana, text="Tratamiento:").pack()
    tratamiento_entry = tk.Entry(informe_ventana)
    tratamiento_entry.pack()

    tk.Label(informe_ventana, text="Informe Médico:").pack()
    informe_entry = tk.Text(informe_ventana, height=10)
    informe_entry.pack()

    def guardar_informe():
        dni_paciente = dni_paciente_entry.get()
        nombre_paciente = nombre_paciente_entry.get()
        informe_texto = informe_entry.get("1.0", tk.END)
        diagnostico = diagnostico_entry.get()
        tratamiento = tratamiento_entry.get()

        # Guardar el informe en Firestore
        ref = db_firestore.collection('pacientes').document(dni_paciente)
        ref.set({
            'dni_paciente': dni_paciente,
            'nombre_paciente': nombre_paciente,
            'informe': informe_texto,
            'diagnostico': diagnostico,
            'tratamiento': tratamiento,
            'medico': nombre_medico,  # Guardar el nombre del médico
            'fecha': datetime.now().strftime('%d/%m/%Y')
        })

        # Crear el PDF
        pdf_file_name = crear_pdf(dni_paciente, nombre_paciente, informe_texto, diagnostico, tratamiento, nombre_medico)

        messagebox.showinfo("Éxito", f"Informe guardado exitosamente. PDF guardado en: {pdf_file_name}")

    tk.Button(informe_ventana, text="Guardar Informe", command=guardar_informe).pack()

# Función para iniciar sesión del médico
def iniciar_sesion():
    dni = dni_entry.get()
    medico = verificar_dni_medico(dni)
    if medico:
        messagebox.showinfo("Éxito", f"Bienvenido {medico['nombre']}")
        abrir_informe_medico(medico['nombre'])  # Pasar el nombre del médico
    else:
        messagebox.showerror("Error", "DNI no encontrado en el sistema")

# Crear ventana principal
root = tk.Tk()
root.title("Inicio de Sesión - Médico")
root.state('zoomed')  # Escalar a pantalla completa

# Etiqueta y campo de entrada para el DNI del médico
tk.Label(root, text="Ingrese su DNI:").pack(pady=10)
dni_entry = tk.Entry(root)
dni_entry.pack(pady=10)

# Botón para iniciar sesión
tk.Button(root, text="Iniciar Sesión", command=iniciar_sesion).pack(pady=10)

# Ejecutar ventana principal
root.mainloop()
