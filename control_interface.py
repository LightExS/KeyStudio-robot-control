from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from serial_communication import change_direction_from_keyboard, send_control_data, serial_port
from dualsense_control import Dualsense
from subprocess import Popen, PIPE
import threading
import signal
import time
import sys
import os


should_connect_to_ble_device = threading.Event()
should_terminate_connection_to_ble_device = threading.Event()
is_app_running = threading.Event()

keys_available = [Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_J, Qt.Key_L]
keys_pressed = [0, 0, 0, 0, 0, 0]  # w, a, s, d, <-, ->
input_mode = 0 # 0 - keyboard, 1 - gamepad joystick, 2 - gamepad accelerometer
mac = ""


class MyApp(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Set up the main layout
        self.initUI()

    def initUI(self) -> None:
        """
        Initializes interface
        """
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
    
    def change_group_clickable(self, state: bool) -> None:
        """
        changes enabled or disabled state for group of elements

        Args:
            state (bool): state to set elements to
        """
        self.disconnect_btn.setEnabled(state)
        self.apply_set_btn.setEnabled(state)
        self.keyboard_rbtn.setEnabled(state)
        self.keyboard_rbtn.setEnabled(state)
        self.gamepad_joy_rbtn.setEnabled(state)
        self.gamepad_accel_rbtn.setEnabled(state)

    def on_connect_btn_click(self) -> None:
        """
        Function called on 'Connect' button pess
        """
        global mac
        
        mac = self.MAC_entry.text()
        should_connect_to_ble_device.set()
        
        self.change_group_clickable(True)

    def on_disconnect_btn_click(self) -> None:
        """
        Function called on 'Disconnect' button pess
        """
        should_terminate_connection_to_ble_device.set()
        self.change_group_clickable(False)

    def on_apply_set_btn_click(self) -> None:
        """
        Function called on 'Apply' button pess
        """
        global input_mode
        if self.keyboard_btn.isChecked():
            input_mode = 0
        elif self.gamepad_joy_btn.isChecked():
            input_mode = 1
        elif self.gamepad_accel_btn.isChecked():
            input_mode = 2
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Key pressess handler

        Args:
            event (QKeyEvent): event of key state change
        """
        if event.isAutoRepeat():
            return
        
        self.change_state_to(event.key(), 1)
        
        change_direction_from_keyboard(keys_pressed)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """
        Key releases handler

        Args:
            event (QKeyEvent): event of key state change
        """
        if event.isAutoRepeat():
            return
        
        self.change_state_to(event.key(), 0)
        
        change_direction_from_keyboard(keys_pressed)
        
    
    def change_state_to(self, key:Qt.Key, state: int) -> None:
        """
        Function to change states of button in keys_available event

        Args:
            key (Qt.Key): key which state was changed
            state (int): was key pressed (1) or unpressed (0)
        """
        for i, k in enumerate(keys_available):
            if key == k:
                keys_pressed[i] = state
                break
    
    def update_distance(self, distance: float) -> None:
        """
        Function to make changes to interface on change of distance

        Args:
            distance (float): distance measured by ultrasonic sensor
        """
        self.distance_label.setText(f"Distance: {distance}")
    
    def on_exit(self) -> None:
        """
        Function called on application exit
        """
        is_app_running.set()
        # listener_thread.join()
        # gamepad_thread.join()
        # serial_thread.join()
        should_terminate_connection_to_ble_device.set()




def ble_listener():
    global mac
    while not is_app_running.is_set():
        if not should_connect_to_ble_device.is_set():
            continue
        should_connect_to_ble_device.clear()

        if mac == "":
            continue
        
        command = ["ble-serial","-d",mac]
        process = Popen(command, stdout=PIPE, stderr=PIPE)

        while not should_terminate_connection_to_ble_device.is_set():
            pass
        
        should_terminate_connection_to_ble_device.clear()
        os.kill(process.pid, signal.SIGINT)



def gamepad_listening():
    global input_mode
    ds = Dualsense()  # open controller
    while not is_app_running.is_set():
        
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
    while not is_app_running.is_set():
        if serial_port.in_waiting:    
            serial_read = serial_port.readline()
            ex.update_distance(float(serial_read))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()   
    app.aboutToQuit.connect(ex.on_exit)
    
    listener_thread = threading.Thread(target=ble_listener)
    gamepad_thread = threading.Thread(target=gamepad_listening)
    serial_thread = threading.Thread(target=serial_reader)
    
    listener_thread.start()
    gamepad_thread.start()
    serial_thread.start()
    
    sys.exit(app.exec_())
    