import time

import batteryTray
import requests_controller

monitor = batteryTray.BatteryMonitor(addr=0x42)


backend = requests_controller.RequestsController(
    endpoint="http://18.116.231.95:8069/odoo-firebase-core/odoo-import",
    access_token="12fa06f23b81d89482ebadc754d20009272e2181e7c8f42759dbafcfd89c9c49",
    account_id=1
)

while True:
    monitor.run()
    battery_data = monitor.get_battery_data()
    print("Haciendo petición...")
    backend.make_request("update_battery_data", battery_data, 1, "ray.rayiot")
    time.sleep(60)

