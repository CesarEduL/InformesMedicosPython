import tkinter as tk
from modules.firebase_module import inicializar_firebase, obtener_firestore
from modules.api_module import cargar_token
from modules.gui_module import iniciar_sesion

# Inicializar Firebase y Firestore
inicializar_firebase()
db_firestore = obtener_firestore()

# Cargar token API
API_TOKEN = cargar_token()

# Crear ventana principal
root = tk.Tk()
root.title("Inicio de Sesión - Médico")
root.state('zoomed')  # Escalar a pantalla completa

# Iniciar sesión del médico
iniciar_sesion(root, db_firestore, API_TOKEN)

# Ejecutar ventana principal
root.mainloop()
