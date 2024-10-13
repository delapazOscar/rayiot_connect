import smbus
import time
import os

# Register Definitions
_REG_CONFIG                 = 0x00
_REG_SHUNTVOLTAGE           = 0x01
_REG_BUSVOLTAGE             = 0x02
_REG_POWER                  = 0x03
_REG_CURRENT                = 0x04
_REG_CALIBRATION            = 0x05

class BusVoltageRange:
    RANGE_16V               = 0x00  # 16V range
    RANGE_32V               = 0x01  # 32V range (default)

class Gain:
    DIV_1_40MV              = 0x00  # Gain 1, 40mV range
    DIV_2_80MV              = 0x01  # Gain 2, 80mV range
    DIV_4_160MV             = 0x02  # Gain 4, 160mV range
    DIV_8_320MV             = 0x03  # Gain 8, 320mV range

class ADCResolution:
    ADCRES_12BIT_1S         = 0x03  # 12-bit, 1 sample

class Mode:
    SANDBVOLT_CONTINUOUS    = 0x07  # Continuous shunt and bus voltage mode

class INA219:
    def __init__(self, i2c_bus=1, addr=0x40):
        self.bus = smbus.SMBus(i2c_bus)
        self.addr = addr

        # Initialize calibration variables
        self._cal_value = 0
        self._current_lsb = 0
        self._power_lsb = 0

        # Set default calibration
        self.set_calibration_16V_1_5A()

    def read(self, address):
        data = self.bus.read_i2c_block_data(self.addr, address, 2)
        return ((data[0] << 8) | data[1])

    def write(self, address, data):
        temp = [data >> 8, data & 0xFF]
        self.bus.write_i2c_block_data(self.addr, address, temp)

    def set_calibration_16V_1_5A(self):
        """Configures INA219 to measure up to 16V and 1.5A of current."""
        MaxExpected_I = 1.5  # 1.5 Amps for peripherals
        
        # 1. Determine Current LSB (45.8 uA per bit)
        self._current_lsb = MaxExpected_I / 32767
        
        # 2. Calculate the calibration value
        calibration_value = int(0.04096 / (self._current_lsb * 0.01))
        self.write(_REG_CALIBRATION, calibration_value)
        
        # 3. Set configuration for 16V, 40mV shunt, 12-bit ADC, continuous mode
        config = (BusVoltageRange.RANGE_16V |
                  Gain.DIV_1_40MV |
                  ADCResolution.ADCRES_12BIT_1S |
                  Mode.SANDBVOLT_CONTINUOUS)
        self.write(_REG_CONFIG, config)
        
        # 4. Calculate power LSB (20 times the current LSB)
        self._power_lsb = 20 * self._current_lsb

    def getShuntVoltage_mV(self):
        value = self.read(_REG_SHUNTVOLTAGE)
        if value > 32767:
            value -= 65536
        return value * 0.01

    def getBusVoltage_V(self):
        value = self.read(_REG_BUSVOLTAGE) >> 3
        return value * 0.004

    def getCurrent_mA(self):
        value = self.read(_REG_CURRENT)
        if value > 32767:
            value -= 65536
        return value * self._current_lsb * 1000  # Convert to mA

    def getPower_W(self):
        value = self.read(_REG_POWER)
        if value > 32767:
            value -= 65536
        return value * self._power_lsb

if __name__ == '__main__':
    # Create an INA219 instance
    ina219 = INA219(i2c_bus=1, addr=0x42)
    
    low = 0
    while True:
        bus_voltage = ina219.getBusVoltage_V()             # Voltage on V- (load side)
        shunt_voltage = ina219.getShuntVoltage_mV() / 1000 # Voltage across the shunt
        current = -ina219.getCurrent_mA() / 1000           # Current in A
        power = ina219.getPower_W()                        # Power in W
        
        # Calculate battery percentage based on the range 6V (0%) to 8.4V (100%)
        p = (bus_voltage - 6) / (8.4 - 6) * 100
        p = max(0, min(p, 100))  # Constrain p between 0% and 100%

        # Print measurements
        print(f"Load Voltage:  {bus_voltage:.3f} V")
        print(f"Current:       {current:.3f} A")
        print(f"Power:         {power:.3f} W")
        print(f"Battery Percent: {p:.1f}%")

        # Shutdown if voltage is below 6V for 30 cycles (~1 minute)
        if bus_voltage < 6.0:
            low += 1
            if low >= 30:  # If voltage stays below 6V for 30 cycles (~1 minute)
                print("System shutdown now due to low voltage")
                os.system("sudo poweroff")
            else:
                print(f"Voltage Low, shutting down in {60-2*low} s")
        else:
            low = 0  # Reset the counter if voltage is above 6V

        print("")
        time.sleep(2)

