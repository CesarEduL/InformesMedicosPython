import json
import requests

# Función para cargar el token desde el archivo config.json
def cargar_token():
    with open('app/config/config.json', 'r') as file:
        config = json.load(file)
    return config['API_TOKEN']

# Función para obtener el nombre del paciente usando la API de la RENIEC
def obtener_nombre_paciente(dni, api_token):
    url = f"https://api.apis.net.pe/v1/dni?numero={dni}"
    headers = {
        'Authorization': f'Bearer {api_token}'
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
