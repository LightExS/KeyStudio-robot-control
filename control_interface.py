from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton
from dualsense_control import Dualsense
from subprocess import Popen, PIPE
from PyQt5.QtCore import Qt
import threading
import serial
import signal
import time
import sys
import os


mac = ""
should_connect_to_ble_device = False
should_terminate_connection_to_ble_device = False
is_app_running = True
current_angle = 90
angle_step = 15
keys_available = [Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_J, Qt.Key_L]
keys_pressed = [0, 0, 0, 0, 0, 0]  # w, a, s, d, <-, ->
input_mode = 0 # 0 - keyboard, 1 - gamepad joystick, 2 - gamepad accelerometer



class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # First row
        self.label = QLabel('Enter MAC address')
        self.MAC_entry = QLineEdit()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.MAC_entry)

        # Second row
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton('connect_btn')
        self.disconnect_btn = QPushButton('disconnect_btn')
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        main_layout.addLayout(button_layout)

        # Third row
        checkbox_layout = QHBoxLayout()
        self.settings_label = QLabel('Settings: ')
        
        self.keyboard_rbtn = QRadioButton('Use Keyboard') 
        self.gamepad_joy_rbtn = QRadioButton('Use Gamepad joystick to turn') 
        self.gamepad_accel_rbtn = QRadioButton('Use Gamepad accelerometer to turn') 
        
        self.keyboard_rbtn.setChecked(True)
        
        checkbox_layout.addWidget(self.settings_label)
        checkbox_layout.addWidget(self.keyboard_rbtn)
        checkbox_layout.addWidget(self.gamepad_joy_rbtn)
        checkbox_layout.addWidget(self.gamepad_accel_rbtn)
        
        main_layout.addLayout(checkbox_layout)

        self.apply_set_btn = QPushButton('apply_set_btn')
        main_layout.addWidget(self.apply_set_btn)

        self.distance_label = QLabel('Distance: ')
        self.distance_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.distance_label)

        # Connect buttons to their respective methods
        self.connect_btn.clicked.connect(self.on_connect_btn_click)
        self.disconnect_btn.clicked.connect(self.on_disconnect_btn_click)
        self.apply_set_btn.clicked.connect(self.on_apply_set_btn_click)
        
        self.change_group_clickable(False)
        
        # Set main layout
        self.setLayout(main_layout)

        self.setWindowTitle('PyQt Layout Example')
        self.setGeometry(300, 300, 400, 300)
        self.show()
    
    def change_group_clickable(self, state):
        self.disconnect_btn.setEnabled(state)
        self.apply_set_btn.setEnabled(state)
        self.keyboard_rbtn.setEnabled(state)
        self.keyboard_rbtn.setEnabled(state)
        self.gamepad_joy_rbtn.setEnabled(state)
        self.gamepad_accel_rbtnn.setEnabled(state)

    def on_connect_btn_click(self):
        global mac, should_connect_to_ble_device
        
        mac = self.MAC_entry.text()
        should_connect_to_ble_device = True
        
        self.change_group_clickable(True)

    def on_disconnect_btn_click(self):
        global should_terminate_connection_to_ble_device
        should_terminate_connection_to_ble_device = True
        self.change_group_clickable(False)

    def on_apply_set_btn_click(self):
        global input_mode
        if self.keyboard_btn.isChecked():
            input_mode = 0
        elif self.gamepad_joy_btn.isChecked():
            input_mode = 1
        elif self.gamepad_accel_btn.isChecked():
            input_mode = 2
        
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        
        self.change_state_to(event.key(), 1)
        
        change_direction()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        
        self.change_state_to(event.key(), 0)
        
        change_direction()
        
    
    def change_state_to(self, key, state):
        for i, k in enumerate(keys_available):
            if key == k:
                keys_pressed[i] = state
                break
    
    def update_distance(self,distance: int):
        self.distance_label.setText(f"Distance: {distance}")
    
    def on_exit(self):
        global is_app_running, should_terminate_connection_to_ble_device
        is_app_running = False
        should_terminate_connection_to_ble_device = True

def send_control_data(left_pwn, left_direction, right_pwn, right_direction, display_direction, servo_angle):
    control_sum = (left_pwn + left_direction + right_pwn + right_direction + display_direction + servo_angle) % 256
    print([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,servo_angle,control_sum])
    #ser.write(bytearray([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,servo_angle,control_sum]))


def change_direction():
    global current_angle, input_mode
    
    if input_mode != 0:
        return
    
    if keys_pressed[4]==1:
        current_angle += angle_step 
    if keys_pressed[5]==1:
        current_angle -= angle_step 
        
    current_angle = min(current_angle,180)
    current_angle = max(current_angle,0)
        
    if sum(keys_pressed[:4]) == 1:
        if keys_pressed[0] == 1:  # w
            send_control_data(200, 1, 200, 1, 0, current_angle)
        elif keys_pressed[1] == 1:  # a
            send_control_data(200, 0, 200, 1, 2, current_angle)
        elif keys_pressed[2] == 1:  # s
            send_control_data(200, 0, 200, 0, 1, current_angle)
        elif keys_pressed[3] == 1:  # d
            send_control_data(200, 1, 200, 0, 3, current_angle)
    elif sum(keys_pressed[:4]) == 2:
        if keys_pressed[0] == 1 and keys_pressed[1] == 1:  # w+a
            send_control_data(40, 1, 255, 1, 0, current_angle)
        elif keys_pressed[0] == 1 and keys_pressed[3] == 1:  # w+d
            send_control_data(255, 1, 40, 1, 0, current_angle)
        elif keys_pressed[2] == 1 and keys_pressed[1] == 1:  # s+a
            send_control_data(40, 0, 255, 0, 1, current_angle)
        elif keys_pressed[2] == 1 and keys_pressed[3] == 1:  # s+d
            send_control_data(255, 0, 40, 0, 1, current_angle)
        else:
            send_control_data(0, 0, 0, 0, 4, current_angle)
    else:
        send_control_data(0, 0, 0, 0, 4, current_angle)


def listener():
    global mac, should_connect_to_ble_device, should_terminate_connection_to_ble_device, is_app_running
    while is_app_running:
        if not should_connect_to_ble_device:
            continue
        should_connect_to_ble_device = False

        if mac == "":
            continue
        
        command = ["ble-serial","-d",mac]
        process = Popen(command, stdout=PIPE, stderr=PIPE)

        while should_terminate_connection_to_ble_device == False:
            pass
        
        should_terminate_connection_to_ble_device = False
        os.kill(process.pid, signal.SIGINT)



def gamepad_listening():
    global input_mode, is_app_running
    ds = Dualsense()  # open controller
    while is_app_running:
        if input_mode == 0:
            continue

        pwn_value, turn = ds.get_trigger_state()
            
        if input_mode == 1:
            right_pwn, left_pwn = ds.get_lj_state(pwn_value)

        elif input_mode == 2:
            right_pwn, left_pwn = ds.get_gyro_state(pwn_value)
            
        
        servo_angle = ds.get_rj_state()
        send_control_data(left_pwn,turn,right_pwn,turn,0,servo_angle)
            
        time.sleep(0.1)
    
    ds.stop()

def serial_reader():
    global is_app_running
    while is_app_running:      
        serial_read = ser.readline()
        ex.update_distance(int(serial_read))

if __name__ == '__main__':
    ser = serial.Serial("COM9")
    app = QApplication(sys.argv)
    ex = MyApp()   
    
    listener_thread = threading.Thread(target=listener)
    gamepad_thread = threading.Thread(target=gamepad_listening)
    serial_thread = threading.Thread(target=serial_reader)
    
    listener_thread.start()
    gamepad_thread.start()
    serial_thread.start()
    
    sys.exit(app.exec_())
    