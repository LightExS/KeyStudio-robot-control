import serial
from pynput.keyboard import Key, Listener, Controller, KeyCode

ser = serial.Serial("COM9")
print(ser.name)

keyboard = Controller()
btns = [
    KeyCode.from_char("w"),
    KeyCode.from_char("a"),
    KeyCode.from_char("s"),
    KeyCode.from_char("d"),
]
keys_pressed = [0, 0, 0, 0]  # w,a,s,d


def send_data(left_pwn, left_direction, right_pwn, right_direction, display_direction):
    ser.write(
        bytearray(
            [left_pwn, left_direction, right_pwn, right_direction, display_direction]
        )
    )


def on_press(key):
    if key == KeyCode.from_char("w"):
        send_data(255, 1, 200, 1, 0)
    if key == KeyCode.from_char("a"):
        send_data(200, 0, 200, 1, 2)
    if key == KeyCode.from_char("s"):
        send_data(200, 0, 200, 0, 1)
    if key == KeyCode.from_char("d"):
        send_data(200, 1, 200, 0, 3)


def on_release(key):
    if key in btns:
        send_data(0, 0, 0, 0, 4)


with Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
    listener.join()


# da
