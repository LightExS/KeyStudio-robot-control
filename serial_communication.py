import serial

current_angle = 0

serial_port = serial.Serial("COM9")


def send_control_data(left_pwn, left_direction, right_pwn, right_direction, display_direction, servo_angle):
    control_sum = (left_pwn + left_direction + right_pwn + right_direction + display_direction + servo_angle) % 256
    print([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,servo_angle,control_sum])
    #serial_port.write(bytearray([255,left_pwn,left_direction,right_pwn,right_direction,display_direction,servo_angle,control_sum]))


def change_direction_from_keyboard(keys_pressed):
    global current_angle
    
    if keys_pressed[4]==1:
        current_angle += 15
    if keys_pressed[5]==1:
        current_angle -= 15
        
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
        