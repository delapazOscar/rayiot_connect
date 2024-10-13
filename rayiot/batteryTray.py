import os
import time
import logging
import INA219

logging.basicConfig(format="%(message)s", level=logging.INFO)


class BatteryMonitor:
    def __init__(self, addr=0x42):
        self.ina = INA219.INA219(addr=addr)
        self.low_voltage_count = 0

    def get_battery_data(self):
        """Obtiene el voltaje, corriente y porcentaje de batería."""
        bus_voltage = self.ina.getBusVoltage_V()  # Voltage en el bus (lado de carga)
        current = -self.ina.getCurrent_mA()  # Corriente en mA
        battery_percentage = self.calculate_battery_percentage(bus_voltage)

        return {
            "voltage": bus_voltage,
            "current": current,
            "battery_percentage": battery_percentage
        }

    def calculate_battery_percentage(self, voltage):
        """Calcula el porcentaje de batería basado en el voltaje."""
        # Considera un rango de 6V (0%) a 8.4V (100%)
        p = (voltage - 6) / (8.4 - 6) * 100
        return max(0, min(p, 100))  # Constrain p between 0% and 100%

    def check_low_voltage(self):
        """Verifica si la batería tiene un voltaje bajo y maneja el apagado si es necesario."""
        battery_data = self.get_battery_data()
        bus_voltage = battery_data["voltage"]

        if bus_voltage < 6.0:
            self.low_voltage_count += 1
            if self.low_voltage_count >= 30:  # Si el voltaje es bajo por 30 ciclos (~1 minuto)
                logging.info("Apagando el sistema debido a bajo voltaje")
                os.system("sudo poweroff")
            else:
                logging.warning(f"Voltaje bajo, apagado en {60 - 2 * self.low_voltage_count} segundos")
        else:
            self.low_voltage_count = 0  # Reinicia el contador si el voltaje es adecuado

    def log_battery_data(self):
        """Imprime y registra los datos de la batería."""
        battery_data = self.get_battery_data()
        logging.info(f"Voltaje: {battery_data['voltage']:.3f} V")
        logging.info(f"Corriente: {battery_data['current']:.3f} mA")
        logging.info(f"Porcentaje de batería: {battery_data['battery_percentage']:.1f}%")

    def run(self):
        """Ejecuta el monitor de batería en un bucle que verifica el estado de la batería cada `check_interval` segundos."""

        self.log_battery_data()
        self.check_low_voltage()



