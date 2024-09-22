from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore, storage, initialize_app
import requests
import pdfkit
from datetime import datetime

# Inicializar Firebase
cred = credentials.Certificate("firebase_config.json")
initialize_app(cred, {'storageBucket': 'tu-bucket.appspot.com'})

db = firestore.client()
bucket = storage.bucket()

app = FastAPI()

# Ruta para crear el informe médico
@app.post("/crear_informe/")
async def crear_informe(data: dict):
    # Validación del médico en la API de la SUNAT
    sunat_response = requests.get(f"https://api.sunat.gob.pe/{data['dni_medico']}")
    if sunat_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Médico no válido")

    # Generar contenido del informe médico (usando plantilla HTML)
    with open('templates/informe_template.html') as f:
        html_content = f.read().format(
            nombre_paciente=data['nombre_paciente'],
            diagnostico=data['diagnostico'],
            tratamiento=data['tratamiento'],
            fecha=datetime.now().strftime('%Y-%m-%d')
        )

    # Convertir el HTML a PDF
    pdf_output_path = f"informes/{data['paciente_id']}.pdf"
    pdfkit.from_string(html_content, pdf_output_path)

    # Subir el informe a Firebase Storage
    blob = bucket.blob(f"informes/{data['paciente_id']}.pdf")
    blob.upload_from_filename(pdf_output_path)

    # Guardar metadatos en Firestore
    doc_ref = db.collection("informes").add({
        "paciente_id": data['paciente_id'],
        "medico_id": data['medico_id'],
        "url": blob.public_url,
        "fecha": firestore.SERVER_TIMESTAMP
    })

    return {"mensaje": "Informe creado correctamente", "url": blob.public_url}

# Ruta para obtener informes médicos por paciente
@app.get("/informes/{paciente_id}")
async def obtener_informes(paciente_id: str):
    informes_ref = db.collection("informes").where('paciente_id', '==', paciente_id).stream()
    informes = [{"id": informe.id, **informe.to_dict()} for informe in informes_ref]
    return informes
