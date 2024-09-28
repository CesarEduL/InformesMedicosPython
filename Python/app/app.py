from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from modules.firebase_module import inicializar_firebase, obtener_firestore, verificar_dni_medico, crear_paciente, verificar_dni_paciente, verificar_dni_admin, get_all_patients, get_all_doctors, get_patient, update_patient, delete_patient_by_dni, crear_medico, get_doctor, update_doctor, delete_doctor_by_dni
from modules.api_module import cargar_token, obtener_nombre_paciente
from modules.pdf_module import crear_pdf
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Inicializar Firebase y Firestore
inicializar_firebase()
db_firestore = obtener_firestore()

# Cargar token API
API_TOKEN = os.environ.get('API_TOKEN', cargar_token())


@app.route('/')
def index():
    if 'user_type' in session:
        if session['user_type'] == 'doctor':
            return redirect(url_for('dashboard'))
        elif session['user_type'] == 'patient':
            return redirect(url_for('patient_dashboard'))
        elif session['user_type'] == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login_user(user_type):
    if request.method == 'POST':
        dni = request.form['dni']
        if user_type == 'doctor':
            user = verificar_dni_medico(dni)
            if user:
                session['user_type'] = 'doctor'
                session['nombre_medico'] = user['nombre']
                session['dni_medico'] = dni
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('dashboard'))
        elif user_type == 'patient':
            user = verificar_dni_paciente(dni)
            if user:
                session['user_type'] = 'patient'
                session['nombre_paciente'] = user['nombre']
                session['dni_paciente'] = dni
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('patient_dashboard'))
        elif user_type == 'admin':
            user = verificar_dni_admin(dni)
            if user:
                session['user_type'] = 'admin'
                session['nombre_admin'] = user['nombre']
                session['dni_admin'] = dni
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('admin_dashboard'))

        flash('DNI no encontrado en el sistema', 'error')
    return render_template(f'login_{user_type}.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/admin_dashboard.html', nombre_admin=session['nombre_admin'])

@app.route('/doctor/dashboard')
def dashboard():
    if 'user_type' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    return render_template('doctor/dashboard.html', nombre_medico=session['nombre_medico'])


@app.route('/patient_dashboard')
def patient_dashboard():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    dni_paciente = session['dni_paciente']
    nombre_paciente = session['nombre_paciente']

    # Obtener los informes médicos del paciente desde Firestore
    informes_query = db_firestore.collection('informes').where(
        'dni_paciente', '==', dni_paciente).stream()

    informes = []
    for informe in informes_query:
        data = informe.to_dict()
        informes.append({
            'title': f"Informe médico",
            'start': datetime.strptime(data['fecha'], '%d/%m/%Y %H:%M:%S').isoformat(),
            'url': url_for('ver_informe', informe_id=informe.id)
        })

    informes_json = json.dumps(informes)

    return render_template('patient/patient_dashboard.html', nombre_paciente=nombre_paciente, informes_json=informes_json)


@app.route('/admin/manage_patients')
def admin_manage_patients():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    patients = get_all_patients()
    return render_template('admin/manage_patients.html', patients=patients)


@app.route('/admin/manage_doctors')
def admin_manage_doctors():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    doctors = get_all_doctors()
    return render_template('admin/manage_doctors.html', doctors=doctors)


@app.route('/admin/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        crear_paciente(dni, nombre)
        flash('Paciente agregado exitosamente', 'success')
        return redirect(url_for('admin_manage_patients'))
    return render_template('admin/add_patient.html')


@app.route('/admin/edit_patient/<string:dni>', methods=['GET', 'POST'])
def edit_patient(dni):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    patient = get_patient(dni)
    if request.method == 'POST':
        nombre = request.form['nombre']
        update_patient(dni, nombre)
        flash('Paciente actualizado exitosamente', 'success')
        return redirect(url_for('admin_manage_patients'))
    return render_template('admin/edit_patient.html', patient=patient)


@app.route('/admin/delete_patient/<string:dni>', methods=['POST'])
def delete_patient(dni):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    delete_patient_by_dni(dni)
    flash('Paciente eliminado exitosamente', 'success')
    return redirect(url_for('admin_manage_patients'))


@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        crear_medico(dni, nombre, especialidad)
        flash('Médico agregado exitosamente', 'success')
        return redirect(url_for('admin_manage_doctors'))
    return render_template('admin/add_doctor.html')


@app.route('/admin/edit_doctor/<string:dni>', methods=['GET', 'POST'])
def edit_doctor(dni):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    doctor = get_doctor(dni)
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        update_doctor(dni, nombre, especialidad)
        flash('Médico actualizado exitosamente', 'success')
        return redirect(url_for('admin_manage_doctors'))
    return render_template('admin/edit_doctor.html', doctor=doctor)


@app.route('/admin/delete_doctor/<string:dni>', methods=['POST'])
def delete_doctor(dni):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    delete_doctor_by_dni(dni)
    flash('Médico eliminado exitosamente', 'success')
    return redirect(url_for('admin_manage_doctors'))

@app.route('/ver_informe/<string:informe_id>')
def ver_informe(informe_id):
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    informe = db_firestore.collection('informes').document(informe_id).get()
    if not informe.exists:
        flash('Informe no encontrado', 'error')
        return redirect(url_for('patient_dashboard'))

    informe_data = informe.to_dict()
    return render_template('patient/ver_informe.html', informe=informe_data)


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

        # Generar un ID único para el informe
        informe_id = f"{dni_paciente}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Guardar el informe en Firestore
        ref = db_firestore.collection('informes').document(informe_id)
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

        # Crear el usuario del paciente en la Realtime Database
        crear_paciente(dni_paciente, nombre_paciente)

        # Crear el PDF
        pdf_file_name = crear_pdf(dni_paciente, nombre_paciente, informe_texto,
                                  diagnostico, tratamiento, session['nombre_medico'])

        return jsonify({'message': 'Informe guardado y paciente registrado exitosamente', 'pdf_file': pdf_file_name})

    return render_template('doctor/informe_medico.html', nombre_medico=session['nombre_medico'])


@app.route('/lista_informes', methods=['GET'])
def lista_informes():
    if 'dni_medico' not in session:
        return redirect(url_for('login'))

    dni_paciente = request.args.get('dni_paciente', None)

    # Obtener los informes del médico actual
    informes_query = db_firestore.collection('informes').where(
        'dni_medico', '==', session['dni_medico'])

    # Si hay un DNI ingresado, filtrar los informes por DNI del paciente
    if dni_paciente:
        informes_query = informes_query.where(
            'dni_paciente', '==', dni_paciente)

    # Ejecutar la consulta y almacenar los informes
    informes = informes_query.stream()
    lista_informes = [{**informe.to_dict(), 'id': informe.id}
                      for informe in informes]

    return render_template('doctor/lista_informes.html', informes=lista_informes)


@app.route('/editar_informe/<string:informe_id>', methods=['GET', 'POST'])
def editar_informe(informe_id):
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))

    ref = db_firestore.collection('informes').document(informe_id)
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

    return render_template('doctor/editar_informe.html', informe=informe.to_dict(), informe_id=informe_id)


@app.route('/borrar_informe/<string:informe_id>', methods=['POST'])
def borrar_informe(informe_id):
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))

    ref = db_firestore.collection('informes').document(informe_id)
    informe = ref.get()

    if not informe.exists:
        flash('Informe no encontrado', 'error')
        return redirect(url_for('lista_informes'))

    # Borrar el informe
    ref.delete()
    flash('Informe borrado exitosamente', 'success')
    return redirect(url_for('lista_informes'))


@app.route('/generar_pdf/<string:informe_id>')
def generar_pdf(informe_id):
    if 'nombre_medico' not in session:
        return redirect(url_for('login'))

    # Obtener los datos del informe desde Firestore
    ref = db_firestore.collection('informes').document(informe_id)
    informe = ref.get()

    if not informe.exists:
        flash('Informe no encontrado', 'error')
        return redirect(url_for('lista_informes'))

    informe_data = informe.to_dict()

    # Crear el PDF
    pdf_file_name = crear_pdf(
        informe_data['dni_paciente'],
        informe_data['nombre_paciente'],
        informe_data['informe'],
        informe_data['diagnostico'],
        informe_data['tratamiento'],
        informe_data['medico']
    )

    # Enviar el archivo PDF al navegador
    return send_file(pdf_file_name, as_attachment=True)

@app.route('/autocompletar_nombre', methods=['POST'])
def autocompletar_nombre():
    dni_paciente = request.form['dni_paciente']
    nombre_paciente = obtener_nombre_paciente(dni_paciente, API_TOKEN)
    if nombre_paciente:
        return jsonify({'nombre_paciente': nombre_paciente})
    else:
        return jsonify({'error': 'No se pudo autocompletar el nombre o DNI no encontrado'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
