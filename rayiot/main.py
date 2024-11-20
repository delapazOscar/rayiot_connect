import time
import threading
from flask import Flask, request, jsonify
import batteryTray
import requests_controller

monitor = batteryTray.BatteryMonitor(addr=0x42)


backend = requests_controller.RequestsController(
    endpoint="https://rayiot.eastus2.cloudapp.azure.com/odoo-firebase-core/odoo-import",
    access_token="12fa06f23b81d89482ebadc754d20009272e2181e7c8f42759dbafcfd89c9c49",
    account_id=1
)

app = Flask(__name__)

# Variable global para almacenar user_id
user_id = None

@app.route('/register_mode', methods=['POST'])
def register_mode():
    """Endpoint para registrar un modo con user_id."""
    global user_id
    data = request.json

    if 'user_id' not in data:
        return jsonify({"error": "user_id es requerido"}), 400

    user_id = data['user_id']
    print(f"user_id recibido: {user_id}")

    # Solicitar NFC ID al usuario
    nfc_id = input("Ingrese el NFC ID: ").strip()

    # Enviar la solicitud al servidor
    try:
        payload = {
            "nfc_id": nfc_id
        }
        backend.make_request(
            method="set_nfc",
            payload=payload,
            res_id=user_id,  # Usar el user_id recibido
            res_model="ray.user"
        )
        return jsonify({"message": "Petición enviada con éxito."}), 200
    except Exception as e:
        print(f"Error al enviar la petición: {e}")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud."}), 500

def run_server():
    """Función para ejecutar el servidor Flask."""
    app.run(host="0.0.0.0", port=5000)

def monitor_device():
    """Función para monitorear el estado del dispositivo y enviar datos."""
    while True:
        monitor.run()
        battery_data = monitor.get_battery_data()
        print("Haciendo petición de estado del dispositivo...")
        try:
            backend.make_request(
                method="update_battery_data",
                payload=battery_data,
                res_id=1,
                res_model="ray.rayiot"
            )
        except Exception as e:
            print(f"Error en la petición: {e}")

        time.sleep(60)

if __name__ == "__main__":
    # Iniciar el servidor Flask en un hilo separado
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Ejecutar el monitoreo del dispositivo en el hilo principal
    print("Servidor Flask escuchando en http://0.0.0.0:5000/register_mode")
    monitor_device()

