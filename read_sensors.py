##*****************************************************************
##TMP117 default configure register
##0b00100010
##0b00100000
##CONV(3 bit, `0b100` by default): Conversion cycle bit. 
##***The last 2 bit of the first byte,
##	and the first 1 bit of the seconnd byte
##AVG(2 bit, `0b01` by default): Conversion averaging modes. 
##	Determines the number of conversion results that are 
##	collected and averaged before updating the temperature 
##	register. The average is an accumulated average and 
##	not a running average.
##	00: No averaging
##	01: 8 Averaged conversions
##	10: 32 averaged conversions
##	11: 64 averaged conversions
##***The second and third bit of the second byte
##*****************************************************************
##CONV[2:0] AVG[1:0] = 00 AVG[1:0] = 01 AVG[1:0] = 10 AVG[1:0] = 11
##000       15.5 ms       125 ms        500 ms        1 s
##001       125 ms        125 ms        500 ms        1 s
##010       250 ms        250 ms        500 ms        1 s
##011       500 ms        500 ms        500 ms        1 s
##100       1 s           1 s           1 s           1 s
##101       4 s           4 s           4 s           4 s
##110       8 s           8 s           8 s           8 s
##111       16 s          16 s          16 s          16 s
##*****************************************************************
from smbus2 import SMBus
from bitarray import bitarray, util
import os
import time
from azure.iot.device import IoTHubDeviceClient, Message

class sensors(object):
    def check_haddress(self, sensor_name, haddress):
        #print(sensor_name, haddress)
        if sensor_name.upper() == 'TMP117':
            if haddress not in (0x48, 0x49, 0x4A, 0x4B):
                print('I2C hardware address is NOT correct! now set it to default 0x48.')
                return 0x48
            else:
                return haddress
        elif sensor_name.upper() == 'SHTC3':
            if haddress != 0x70:
                print('I2C hardware address is NOT correct! now set it to default 0x70.')
                return 0x70
            else:
                return haddress
        else:
            return haddress

class TMP117(sensors):
    temp_max_value = 50
    temp_min_value = -20
    sensor_temperature_register = 0x00
    sensor_configure_register = 0x01

    def __init__(self, haddress=0x48, i2c_channel=1):
        self.hadd = haddress
        self.hadd = sensors.check_haddress(self, 'TMP117', self.hadd)
        self.i2c_ch = i2c_channel
        #self.bus = SMBus(self.i2c_ch)

    def set_haddress(self, new_haddress):
        self.hadd = new_haddress
        self.check_haddress()

    def get_haddress(self):
        return self.hadd

    def sensor_configure(self, conv=0b100, avg=0b01):
        with SMBus(self.i2c_ch) as bus:
            #read the configure register
            #print(self.hadd, self.sensor_configure_register)
            conf = bus.read_i2c_block_data(self.hadd, self.sensor_configure_register, 2)
            print("Old CONFIG:", conf)
            #high8 = util.int2ba(conf[0], 8)[:6] + util.int2ba(conv, 3)[:2]
            #low8 = util.int2ba(conv, 3)[2:] + util.int2ba(avg, 2) + util.int2ba(conf[1], 8)[3:]
            #print(high8, low8)
            conf[0] = util.ba2int(util.int2ba(conf[0], 8)[:6] + util.int2ba(conv, 3)[:2])
            conf[1] = util.ba2int(util.int2ba(conv, 3)[2:] + util.int2ba(avg, 2) + util.int2ba(conf[1], 8)[3:])
            #print(conf)
            bus.write_i2c_block_data(self.hadd, self.sensor_configure_register, conf)
            conf = bus.read_i2c_block_data(self.hadd, self.sensor_configure_register, 2)
            print("New CONFIG:", conf)

    def read_temp(self):
        with SMBus(self.i2c_ch) as bus:
            temp_val = bus.read_i2c_block_data(self.hadd, self.sensor_temperature_register, 2)
            return ((temp_val[0] << 8) | (temp_val[1])) * 0.0078125

    def most_acc_limit(self):
        if self.read_temp() > self.temp_max_value or self.read_temp() < self.temp_min_value:
            return False
        return True

class SHTC3(sensors):
    dev_reg = '/sys/bus/i2c/devices/i2c-1/new_device'
    dev_reg_param = 'shtc1 0x70'
    dev_temp = '/sys/class/hwmon/hwmon1/temp1_input'
    dev_humd = '/sys/class/hwmon/hwmon1/humidity1_input'

##    def __init__(self, haddress=0x70, i2c_channel=1):
##        self.hadd = haddress
##        self.hadd = super.check_haddress('SHTC3', self.hadd)
##        self.i2c_ch = i2c_channel

    def dev_reg(self):
        if not os.path.isfile(self.dev_temp) and not os.path.isfile(self.dev_humd):
            with open(self.dev_reg, 'wb') as f:
                f.write(self.dev_reg_param)

    def read_data(self):
        with open(self.dev_temp, 'rb') as f:
            val = f.read().strip()
            temperature = float(int(val)) / 1000
        with open(self.dev_humd, 'rb') as f:
            val = f.read().strip()
            humidity = float(int(val)) / 1000
        return (temperature, humidity)

class AzureIoTHub(object):
    CONNECTION_STRING = 'HostName=IIoTLearning.azure-devices.net;DeviceId=sensors952;SharedAccessKey=fTmYrxuY20aVpfb3HezoQMu2aF2X+nKmEL0aFzHiHnI='
    MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity}}}'

    def __init__(self):
        # Create an IoT Hub client
        self.client = IoTHubDeviceClient.create_from_connection_string(self.CONNECTION_STRING)

    def iothub_client_telemetry_run(self, temperature, humidity):
        # Build the message with temperature and humidity values.
        msg_txt_formatted = self.MSG_TXT.format(temperature=temperature, humidity=humidity)
        message = Message(msg_txt_formatted)
        #print("Sending message: {}".format(message))
        try:
            self.client.send_message(message)
            print ("Message successfully sent.")
        except:
            print ("Fail to sent message.")


def main():
    tmp117 = TMP117()
    shtc3 = SHTC3()
    tmp117.sensor_configure(0b011, 0b01)  #set to 500ms
    shtc3.dev_reg()
    azure_iothub_client = AzureIoTHub()
    try:
        while True:
            temperature = tmp117.read_temp()
            humidity = shtc3.read_data()[1]
            print('Temperature: ' + str(temperature) + ' | Humidity: ' + str(humidity) + ' | Time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            azure_iothub_client.iothub_client_telemetry_run(temperature, humidity)
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopped read data from sensors.')

if __name__ == '__main__':
    main()
