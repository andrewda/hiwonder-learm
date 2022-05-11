from .util import Util

class Servo:
    def __init__(self,
                 servo_id,
                 min_position=500,
                 max_position=2500,
                 start_position=1500):
        assert min_position <= max_position
        assert start_position >= min_position and start_position <= max_position

        self.servo_id = servo_id
        self.min_position = min_position
        self.max_position = max_position

        self.__set_position(start_position)


    def __get_position(self):
        return self.__position


    def __set_position(self, position):
        assert position >= self.min_position and position <= self.max_position
        self.__position = int(position)


    position = property(__get_position, __set_position)
