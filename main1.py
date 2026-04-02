import calc
from gpiozero import Motor, Button
import keyboard
import select
import time
import threading
#constants
actuator_time_scaling = 1
motor_time_scaling = 1
reset_motor_time = 1
reset_actuator_time = 1
#flags
manual_mode = False
stopped = False
#hardware
motor = Motor(forward=12, backward=20)
actuator = Motor(forward=6, backward=5)
start = Button(1)
stop = Button(1)
manual = Button(1)

def stop_brushing():
    stopped = True
    print("Stopping..")
def toggle_mode():
    manual_mode = not manual_mode
    if manual_mode:
        print("Switched to manual mode (press start each time)")
    else:
        print("Switched to automatic mode")
stop.when_pressed = stop_brushing
manual.when_pressed = toggle_mode

def actuator_step(step_num):
    d_length = calc.table[step_num][2]                    # get change in distance(mm) for current interval
    if d_length > 0:
        print("actuator +"+str(round(d_length),1)+"mm", end=" ")    #don't start new line at the end before motor info
        actuator.forward()
    else:
        print("actuator -"+str(round(-d_length),1)+"mm", end=" ")
        actuator.backward()
    time.sleep(abs(d_length) * actuator_time_scaling)
    actuator.stop()
def motor_step(step_num):
    d_angle = calc.table[step_num][3]                     # get change in angle(rad) for current interval
    if d_angle > 0:
        print("motor: +", round(d_angle,2), "rad")
        motor.forward()
    else:
        print("motor: -", round(-d_angle,2), "rad")
        motor.backward()
    time.sleep(abs(d_angle) * motor_time_scaling)
    motor.stop()
def arm_step(step_num):
    actuator_task = threading.Thread(target=actuator_step, args=[step_num])        # threading lets motors be controlled separately
    motor_task = threading.Thread(target=motor_step, args=[step_num])
    actuator_task.start()
    motor_task.start()
    actuator_task.join()
    motor_task.join()
    time.sleep(0.2)
def brush_movement():
    for step_num in range(1, 20):
        print("Step " + str(step_num) + "/20:", end=" ")           #starts the line, "Step 1/20: actuator +1.2mm motor -0.67 rad"
        arm_step(step_num)
        if stopped:
            return

def reset_position():
    print("Resetting...", end="")
    motor.backward()
    time.sleep(reset_motor_time)
    actuator.backward()
    time.sleep(reset_actuator_time)
    print("done")
def setup():                                                            # user controls arm to initial position
    calc.init_lookup_table()                                            # generate table of angles and lengths from parametric curve
    stopped = False
    print("Control arm length with w/s, angle with a/d, use Start to begin brushing.")
    while (True):
        if keyboard.is_pressed('w'):
            print("Actuator forward...", end="\r")                             #overwrite these in the same spot
            motor.stop()
            actuator.forward()
        elif keyboard.is_pressed('s'):
            print("Actuator reverse...", end="\r")
            motor.stop()
            actuator.backward()
        elif keyboard.is_pressed('a'):
            print("Motor reverse...   ", end="\r")
            actuator.stop()
            motor.backward()
        elif keyboard.is_pressed('d'):
            print("Motor forward...   ", end="\r")
            actuator.stop()
            motor.forward()
        elif start.is_pressed:
            actuator.stop()
            motor.stop()
            print("Setup complete.")
            break
        time.sleep(0.05)

def main():
    while (True):
        print("Press Start to begin setting up.")
        start.wait_for_press()
        setup()
        while (stopped == False):
            brush_movement()
            if (manual_mode):
                print("pausing...\r")
                while (not start.is_pressed && not stopped):
                    time.sleep(0.5)
            if (stopped):
                break
            reset_position()
        print("brush buddy finished.", end=" ")                        # "brush buddy finished. press start..."

try:
    main()
except KeyboardInterrupt:
    print("done")
