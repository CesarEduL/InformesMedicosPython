import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from modules.pdf_module import crear_pdf
from modules.api_module import obtener_nombre_paciente
from modules.firebase_module import verificar_dni_medico

# Función para abrir la ventana de informe médico
def abrir_informe_medico(root, nombre_medico, db_firestore, api_token):
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
        nombre_paciente = obtener_nombre_paciente(dni_paciente, api_token)
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
def iniciar_sesion(root, db_firestore, api_token):
    def iniciar():
        dni = dni_entry.get()
        medico = verificar_dni_medico(dni)
        if medico:
            messagebox.showinfo("Éxito", f"Bienvenido {medico['nombre']}")
            abrir_informe_medico(root, medico['nombre'], db_firestore, api_token)
        else:
            messagebox.showerror("Error", "DNI no encontrado en el sistema")

    dni_entry = tk.Entry(root)
    dni_entry.pack(pady=10)
    tk.Button(root, text="Iniciar Sesión", command=iniciar).pack(pady=10)
