from pydualsense import pydualsense, TriggerModes
import time


def cross_pressed(state):
    print(state)


def joystick(stateX, stateY):
    print(ds.states)


ds = pydualsense()  # open controller
ds.init()  # initialize controller

ds.cross_pressed += cross_pressed
ds.left_joystick_changed += joystick
ds.light.setColorI(255, 0, 0)  # set touchpad color to red

ds.triggerL.setMode(TriggerModes.Rigid)
ds.triggerL.setForce(1, 40)
ds.triggerR.setMode(TriggerModes.Rigid)
ds.triggerR.setForce(1, 40)

while not ds.state.R1:
    pass

ds.close()  # closing the controller
