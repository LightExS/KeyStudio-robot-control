import serial
from pynput.keyboard import Listener, Controller, KeyCode, Key
import threading
import time
import os

current_angle = 90
angle_step = 15

ser = serial.Serial("COM9")


keyboard = Controller()
prev_pressed = [0, 0, 0, 0, 0, 0]  # w, a, s, d, <-, ->
keys_pressed = [0, 0, 0, 0, 0, 0]  # w, a, s, d, <-, ->


def send_control_data(left_pwn, left_direction, right_pwn, right_direction, display_direction):
    global current_angle
    control_sum = (left_pwn + left_direction + right_pwn + right_direction + display_direction + current_angle) % 256
    print(control_sum)
    ser.write(bytearray([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,current_angle,control_sum]))



def change_direction():
    global current_angle
    
    print(keys_pressed, current_angle)
    if keys_pressed[4]==1:
        current_angle += angle_step 
    if keys_pressed[5]==1:
        current_angle -= angle_step 
        
    current_angle = min(current_angle,180)
    current_angle = max(current_angle,0)
        
    if sum(keys_pressed[:4]) == 1:
        if keys_pressed[0] == 1:  # w
            send_control_data(200, 1, 200, 1, 0)
        elif keys_pressed[1] == 1:  # a
            send_control_data(200, 0, 200, 1, 2)
        elif keys_pressed[2] == 1:  # s
            send_control_data(200, 0, 200, 0, 1)
        elif keys_pressed[3] == 1:  # d
            send_control_data(200, 1, 200, 0, 3)
    elif sum(keys_pressed[:4]) == 2:
        if keys_pressed[0] == 1 and keys_pressed[1] == 1:  # w+a
            send_control_data(40, 1, 255, 1, 0)
        elif keys_pressed[0] == 1 and keys_pressed[3] == 1:  # w+d
            send_control_data(255, 1, 40, 1, 0)
        elif keys_pressed[2] == 1 and keys_pressed[1] == 1:  # s+a
            send_control_data(40, 0, 255, 0, 0)
        elif keys_pressed[2] == 1 and keys_pressed[3] == 1:  # s+d
            send_control_data(255, 0, 40, 0, 0)
        else:
            send_control_data(0, 0, 0, 0, 4)
    else:
        send_control_data(0, 0, 0, 0, 4)


def on_press(key):
    global current_angle,prev_pressed
    prev_pressed = keys_pressed.copy()
    
    
    if key == KeyCode.from_char("w"):
        keys_pressed[0] = 1
    if key == KeyCode.from_char("a"):
        keys_pressed[1] = 1
    if key == KeyCode.from_char("s"):
        keys_pressed[2] = 1
    if key == KeyCode.from_char("d"):
        keys_pressed[3] = 1

    if key == Key.left:
        keys_pressed[4] = 1
    if key == Key.right:
        keys_pressed[5] = 1

    if prev_pressed != keys_pressed:
        change_direction()


def on_release(key):
    if key == KeyCode.from_char("w"):
        keys_pressed[0] = 0
    if key == KeyCode.from_char("a"):
        keys_pressed[1] = 0
    if key == KeyCode.from_char("s"):
        keys_pressed[2] = 0
    if key == KeyCode.from_char("d"):
        keys_pressed[3] = 0
    
    if key == Key.left:
        keys_pressed[4] = 0
    if key == Key.right:
        keys_pressed[5] = 0

    change_direction()


def open_connection():
    os.system("ble-serial -d 48:70:1E:9F:66:F1")


def start_listening():
    with Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
        listener.join()


def some_other_task():
    while True:      
        print(ser.readline())
        time.sleep(0.1)
        # print("Running another task in parallel...")


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
