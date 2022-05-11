from .servo import Servo
import time


class Controller:
    SIGNATURE = 0x55
    CMD_SERVO_MOVE = 0x03
    CMD_GET_BATTERY_VOLTAGE = 0x0f
    CMD_SERVO_STOP = 0x14
    CMD_GET_SERVO_POSITION = 0x15


    def __init__(self, com_port, debug=False):
        if com_port.startswith('COM'):
            import serial
            self._device = serial.Serial(com_port, 9600, timeout = 1)
            self._is_serial = True
        elif com_port.startswith('USB'):
            import hid
            self._device = hid.device()
            serial_number = com_port.strip('USB')
            if serial_number:
                self._device.open(0x0483, 0x5750, serial_number)
            else:
                self._device.open(0x0483, 0x5750)
            self._device.set_nonblocking(1)
            if debug:
                print('Serial number:', self._device.get_serial_number_string())
            self._usb_recv_event = False
            self._is_serial = False
        else:
            raise ValueError('Invalid COM port')
        self.debug = debug
        self._input_report = []


    def setPosition(self, servos, duration=1000, wait=False):
        data = bytearray([1, duration & 0xff, (duration & 0xff00) >> 8])

        if isinstance(servos, Servo):
            data.extend([servos.servo_id, servos.position & 0xff, (servos.position & 0xff00) >> 8])
        elif isinstance(servos, list) and all(isinstance(x, Servo) for x in servos):
            data[0] = len(servos)
            for servo in servos:
                data.extend([servo.servo_id, servo.position & 0xff, (servo.position & 0xff00) >> 8])
        else:
            raise ValueError('Invalid servos provided')

        self._send(self.CMD_SERVO_MOVE, data)

        if wait:
            time.sleep(duration / 1000)


    def getPosition(self, servos):
        if isinstance(servos, Servo):
            data = bytearray([1, servos.servo_id])
        elif isinstance(servos, list) and all(isinstance(x, Servo) for x in servos):
            data = bytearray([len(servos)])
            for servo in servos:
                data.append(servo.servo_id)
        else:
            raise ValueError('Invalid servos provided')

        self._send(self.CMD_GET_SERVO_POSITION, data)

        data = self._recv(self.CMD_GET_SERVO_POSITION)

        if data != None:
            if isinstance(servos, list):
                values = map(lambda i: data[i * 3 + 3] * 256 + data[i * 3 + 2], zip(data[0]))
                return list(values)
            else:
                position = data[3] * 256 + data[2]
                return position
        else:
            raise Exception('Error getting servo position')


    def servoOff(self, servos=None):
        data = bytearray([1])

        if isinstance(servos, Servo):
            data.append(servos.servo_id)
        elif isinstance(servos, list) and all(isinstance(x, Servo) for x in servos):
            data[0] = len(servos)
            for servo in servos:
                data.append(servo.servo_id)
        elif servos == None:
            data = [6, 1,2,3,4,5,6]
        else:
            raise ValueError('Invalid servos provided')

        self._send(self.CMD_SERVO_STOP, data)


    def getBatteryVoltage(self):
        self._send(self.CMD_GET_BATTERY_VOLTAGE)
        data = self._recv(self.CMD_GET_BATTERY_VOLTAGE)

        if data != None:
            return (data[1] * 256 + data[0]) / 1000.0
        else:
            return None


    def _send(self, cmd, data = []):
        if self.debug:
            print('Send Data (' + str(len(data)) + '): ' + ' '.join('{:02x}'.format(x) for x in data))

        if self._is_serial:
            self._device.flush()
            self._device.write([self.SIGNATURE, self.SIGNATURE, len(data) + 2, cmd])
            if len(data) > 0:
                self._device.write(data)
        else:  # Is USB
            report_data = [
                0,
                self.SIGNATURE,
                self.SIGNATURE,
                len(data) + 2,
                cmd
            ]
            if len(data):
                report_data.extend(data)
            self._usb_recv_event = False
            self._device.write(report_data)


    def _recv(self, cmd):
        if self._is_serial:
            data = self._device.read(4)

            if self.debug:
                print('Recv Data: ' + ' '.join('{:02x}'.format(x) for x in data), end=" ")

            if data[0] == self.SIGNATURE and data[1] == self.SIGNATURE and data[3] == cmd:
                length = data[2]
                data = self._device.read(length)

                if self.debug:
                    print(' '.join('{:02x}'.format(x) for x in data))

                return data
            else:
                return None
        else:  # Is USB
            self._input_report = self._device.read(255)

            if self.debug:
                print(self._input_report)

            if self._input_report[0] == self.SIGNATURE and self._input_report[1] == self.SIGNATURE and self._input_report[3] == cmd:
                length = self._input_report[2]
                data = self._input_report[4:4 + length]
                if self.debug:
                    print('Recv Data: ' + ' '.join('{:02x}'.format(x) for x in data))
                return data
            return None
