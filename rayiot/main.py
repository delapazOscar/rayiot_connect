import time

import batteryTray
import requests_controller

monitor = batteryTray.BatteryMonitor(addr=0x42)
monitor.run(check_interval=60)  # Verifica cada 60 segundos

requests = requests_controller.RequestsController(
    "http://18.116.231.95:8069/odoo-firebase-core/odoo-import",
    "12fa06f23b81d89482ebadc754d20009272e2181e7c8f42759dbafcfd89c9c49",
    1
)

while True:
    battery_data = monitor.get_battery_data()
    print("Haciendo petición...")
    requests.make_request("update_battery_data", battery_data, 1, "ray.rayiot")
    time.sleep(60)

