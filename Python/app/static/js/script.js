document.addEventListener('DOMContentLoaded', function() {
    const autocompletarBtn = document.getElementById('autocompletarNombre');
    const informeForm = document.getElementById('informeForm');
    const mensajeDiv = document.getElementById('mensaje');

    function showMessage(message, isError = false) {
        mensajeDiv.textContent = message;
        mensajeDiv.classList.add('fade-in');
        mensajeDiv.classList.toggle('text-red-600', isError);
        mensajeDiv.classList.toggle('text-green-600', !isError);
        setTimeout(() => mensajeDiv.classList.remove('fade-in'), 500);
    }

    if (autocompletarBtn) {
        autocompletarBtn.addEventListener('click', function() {
            const dniPaciente = document.getElementById('dni_paciente').value;
            if (!dniPaciente) {
                showMessage('Por favor, ingrese el DNI del paciente.', true);
                return;
            }
            
            autocompletarBtn.disabled = true;
            autocompletarBtn.classList.add('opacity-50');
            fetch('/autocompletar_nombre', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `dni_paciente=${dniPaciente}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.nombre_paciente) {
                    document.getElementById('nombre_paciente').value = data.nombre_paciente;
                    showMessage('Nombre autocompletado exitosamente.');
                } else {
                    showMessage('No se pudo autocompletar el nombre o DNI no encontrado.', true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error al autocompletar el nombre.', true);
            })
            .finally(() => {
                autocompletarBtn.disabled = false;
                autocompletarBtn.classList.remove('opacity-50');
            });
        });
    }

    if (informeForm) {
        informeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(informeForm);
            const submitBtn = informeForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50');
            fetch('/informe_medico', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                showMessage(data.message);
                if (data.pdf_file) {
                    showMessage(`${data.message} PDF guardado en: ${data.pdf_file}`);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error al guardar el informe.', true);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-50');
            });
        });
    }
});