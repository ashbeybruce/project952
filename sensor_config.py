TMP117_TEMP_REGISTER = 0x00
TMP117_CONF_REGISTER = 0x01
TEMP_MAX_VALUE = 50
TEMP_MIX_VALUE = -20
TMP117_RESOLUTION = 0.0078125

SHTC3_TEMP = '/sys/class/hwmon/hwmon1/temp1_input'
SHTC3_HUMD = '/sys/class/hwmon/hwmon1/humidity1_input'
SHTC3_REG = '#!/bin/bash\nsudo su <<EOF\necho shtc1 0x70 > /sys/bus/i2c/devices/i2c-1/new_device\nexit\nEOF'

MAX_SHOWDATA_NUMBER = 20
TEMP_SHOW_SCALE = 0.01
HUMD_SHOW_SCALE = 0.1
