import serial
import threading
import time
import os
from pydualsense import pydualsense

ser = serial.Serial("COM9")
prev_sum = 0

def mapFromTo(x, range1, range2):
    y = (x - range1[0]) / (range1[1] - range1[0]) * (range2[1] - range2[0]) + range2[0]
    return y

def send_control_data(left_pwn, left_direction, right_pwn, right_direction, display_direction,servo_angle,control_sum):
    ser.write(bytearray([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,servo_angle,control_sum]))



def open_connection():
    os.system("ble-serial -d 48:70:1E:9F:66:F1")


def start_listening():
    ds = pydualsense()  # open controller
    ds.init()  # initialize controller
    while True:
        left_pwn = ds.state.R2 - ds.state.L2
        right_pwn = left_pwn
        
        if left_pwn < 0:
            left_pwn = -left_pwn
            right_pwn = -right_pwn
            turn = 0
        else:
            turn = 1
        
        turn_percent = mapFromTo(abs(ds.state.LX)*2, (0, 256), (0, 1))
        turn_value = left_pwn * turn_percent
        #print(turn_value)
        if ds.state.LX > 0:
            right_pwn -= turn_value
            left_pwn += turn_value
        else:
            left_pwn -= turn_value
            right_pwn += turn_value
        
        left_pwn = int(min(left_pwn,255))
        right_pwn = int(min(right_pwn,255))
        
        servo_angle = int(mapFromTo(ds.state.RX, (128, -128), (0, 180)))
        
        control_sum = (left_pwn + turn + right_pwn + turn + servo_angle) % 256
        send_control_data(left_pwn,turn,right_pwn,turn,0,servo_angle,control_sum)
            
        time.sleep(0.1)


def some_other_task():
    while True:
        print(ser.readline())
        time.sleep(0.1)


if __name__ == "__main__":
    # Create threads for pynput listener and another task
    listener_thread = threading.Thread(target=start_listening)
    other_task_thread = threading.Thread(target=some_other_task)
    open_connection_thread = threading.Thread(target=open_connection)

    # Start the threads
    open_connection_thread.start()
    listener_thread.start()
    other_task_thread.start()

    # Wait for both threads to complete
    open_connection_thread.join()
    listener_thread.join()
    other_task_thread.join()
