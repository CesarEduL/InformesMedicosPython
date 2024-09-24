from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from modules.firebase_module import inicializar_firebase, obtener_firestore, verificar_dni_medico
from modules.api_module import cargar_token, obtener_nombre_paciente
from modules.pdf_module import crear_pdf
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar Firebase y Firestore
inicializar_firebase()
db_firestore = obtener_firestore()

# Cargar token API
API_TOKEN = cargar_token()

@app.route('/')
def index():
    if 'nombre_medico' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni = request.form['dni']
        medico = verificar_dni_medico(dni)
        if medico:
            session['nombre_medico'] = medico['nombre']
            session['dni_medico'] = dni
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('DNI no encontrado en el sistema', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', nombre_medico=session['nombre_medico'])

@app.route('/informe_medico', methods=['GET', 'POST'])
def informe_medico():
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        dni_paciente = request.form['dni_paciente']
        nombre_paciente = request.form['nombre_paciente']
        diagnostico = request.form['diagnostico']
        tratamiento = request.form['tratamiento']
        informe_texto = request.form['informe']

        # Guardar el informe en Firestore
        ref = db_firestore.collection('pacientes').document(dni_paciente)
        ref.set({
            'dni_paciente': dni_paciente,
            'nombre_paciente': nombre_paciente,
            'informe': informe_texto,
            'diagnostico': diagnostico,
            'tratamiento': tratamiento,
            'medico': session['nombre_medico'],
            'dni_medico': session['dni_medico'],
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })

        # Crear el PDF
        pdf_file_name = crear_pdf(dni_paciente, nombre_paciente, informe_texto, diagnostico, tratamiento, session['nombre_medico'])

        return jsonify({'message': 'Informe guardado exitosamente', 'pdf_file': pdf_file_name})

    return render_template('informe_medico.html', nombre_medico=session['nombre_medico'])

@app.route('/lista_informes')
def lista_informes():
    if 'dni_medico' not in session:
        return redirect(url_for('login'))
    
    # Obtain all reports for the current doctor
    informes = list(db_firestore.collection('pacientes').where('dni_medico', '==', session['dni_medico']).stream())
    lista_informes = [{**informe.to_dict(), 'id': informe.id} for informe in informes]
    
    return render_template('lista_informes.html', informes=lista_informes)

@app.route('/editar_informe/<string:dni_paciente>', methods=['GET', 'POST'])
def editar_informe(dni_paciente):
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))
    
    ref = db_firestore.collection('pacientes').document(dni_paciente)
    informe = ref.get()
    
    if not informe.exists:
        flash('Informe no encontrado', 'error')
        return redirect(url_for('lista_informes'))
    
    if request.method == 'POST':
        # Actualizar el informe
        ref.update({
            'nombre_paciente': request.form['nombre_paciente'],
            'diagnostico': request.form['diagnostico'],
            'tratamiento': request.form['tratamiento'],
            'informe': request.form['informe'],
            'fecha_actualizacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        flash('Informe actualizado exitosamente', 'success')
        return redirect(url_for('lista_informes'))
    
    return render_template('editar_informe.html', informe=informe.to_dict(), dni_paciente=dni_paciente)

@app.route('/autocompletar_nombre', methods=['POST'])
def autocompletar_nombre():
    dni_paciente = request.form['dni_paciente']
    nombre_paciente = obtener_nombre_paciente(dni_paciente, API_TOKEN)
    if nombre_paciente:
        return jsonify({'nombre_paciente': nombre_paciente})
    else:
        return jsonify({'error': 'No se pudo autocompletar el nombre o DNI no encontrado'}), 400

if __name__ == '__main__':
    app.run(debug=True)