from fpdf import FPDF
from datetime import datetime
import os

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
