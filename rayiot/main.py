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

monitor_device()

