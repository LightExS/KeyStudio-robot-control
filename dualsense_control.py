import pydualsense

def mapFromTo(x, range1, range2):
    y = (x - range1[0]) / (range1[1] - range1[0]) * (range2[1] - range2[0]) + range2[0]
    return y

class Dualsense:
    def __init__(self):
        self.ds = pydualsense.pydualsense()
        self.ds.init()
    def get_trigger_state(self) -> list[int ,int]:
        """
        Function to retrieve values from right and left triggers to determine pwn_value and turn

        Returns:
            list[int ,int]: [pwn_value, turn] where: 
            pwn_value - is the value that is sent to electromotors
            turn - tells which side motors have to turn 1 being forward and 0 backwards
        """
        left_pwn = self.ds.state.R2 - self.ds.state.L2
        
        if left_pwn < 0:
            left_pwn = -left_pwn
            turn = 0
        else:
            turn = 1
        
        return (left_pwn,turn)
    
    def get_lj_state(self, pwn_value: int) -> list[int ,int]:
        """
        Function to retrieve values from left joystick and using previously calculated value that is put on electromotors determine how much to add or subtract from left and right electomotors to make it turn correctly and return those values

        Args:
            pwn_value (int): value that is forwarded to electromotors

        Returns:
            list[int ,int]: returns values that correspond to what should be forwarded to left and right_pwns (int that order)
        """
        turn_percent = mapFromTo(abs(self.ds.state.LX), (0, 128), (0, 1))
        turn_value = pwn_value * turn_percent
        
        if self.ds.state.LX > 0:
            left_pwn = int(min(pwn_value + turn_value,255))
            right_pwn = int(min(pwn_value - turn_value,255))
        else:
            left_pwn = int(min(pwn_value - turn_value,255))
            right_pwn = int(min(pwn_value + turn_value,255))
        
        return [left_pwn, right_pwn]
    
    def get_gyro_state(self, pwn_value: int ) -> list[int ,int]:
        """
        Function to retrieve values from gyroscope and using previously calculated value that is put on electromotors determine how much to add or subtract from left and right electomotors to make it turn correctly and return those values

        Args:
            pwn_value (int): value that is forwarded to electromotors

        Returns:
            list[int ,int]: returns values that correspond to what should be forwarded to left and right_pwns (int that order)
        """
        gyro_value = min(abs(self.ds.state.gyro.Pitch), 5000)
        turn_percent = mapFromTo(gyro_value, (0, 5000), (0, 1))
        turn_value = pwn_value * turn_percent
    
        if self.ds.state.gyro.Pitch < 0:
            left_pwn = int(min(pwn_value + turn_value,255))
            right_pwn = int(min(pwn_value - turn_value,255))
        else:
            left_pwn = int(min(pwn_value - turn_value,255))
            right_pwn = int(min(pwn_value + turn_value,255))
        
        return [left_pwn, right_pwn]

    def get_rj_state(self) -> int:
        """
        Function to retrieve values from right joystick, map it to range(0,180) and return it

        Returns:
            int: value that should be forwarded to servo
        """
        return int(mapFromTo(self.ds.state.RX, (128, -128), (0, 180)))

    def change_color(self, color: tuple[int, int, int]) -> None:
        """
        Function to change color of touchpad

        Args:
            color (tuple[int, int, int]): tuple of rgb coded color
        """
        self.ds.light.setColorI(*color)
    
    def stop(self) -> None:
        """
        Function to disconnect from gamepad
        """
        self.ds.close()
        

    