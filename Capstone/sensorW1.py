from w1thermsensor import W1ThermSensor, Unit

sensor = W1ThermSensor()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(Unit.DEGREES_F)
temperature_in_all_units = sensor.get_temperatures([
    Unit.DEGREES_C,
    Unit.DEGREES_F,
    Unit.KELVIN])