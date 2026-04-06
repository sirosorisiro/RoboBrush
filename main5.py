import calc
from gpiozero import Motor, Button
import time
import threading

# constants
actuator_time_scaling = 0.6 # <2 
motor_time_scaling = 5
reset_motor_time = 1.5
reset_actuator_time = 5

# flags
manual_mode = True
stopped = False

motor = Motor(forward=20, backward=12)
actuator = Motor(forward=5, backward=6)
start = Button(2, bounce_time = 0.05)
stop = Button(3, bounce_time = 0.05)
mode = Button(4, bounce_time = 0.05)
motorspeed = 0.65

# button functions
def stop_brushing():
    global stopped
    stopped = True
    print("Stopping..")


def toggle_mode():
    global manual_mode
    manual_mode = not manual_mode
    if manual_mode:
        print("Switched to manual resets")
    else:
        print("Switched to automatic resets")


def actuator_step(step_num):
    d_length = calc.table[step_num][2]  # get change in length for current interval
    print("Step (%d)/20: (%+.1f)mm " % (step_num, d_length), end="")  # format into "Step 1/20: +1.2mm ..."
    if d_length > 0:
        actuator.forward()
    else:
        actuator.backward()
    time.sleep(actuator_time_scaling)
    actuator.stop()


def motor_step(step_num):
    d_angle = calc.table[step_num][3]  # get change in angle for current interval
    print("(%+.2f)rad" % d_angle, end="\r")  # format into "...-0.34rad", write over the same line for less clutter
    if d_angle > 0:
        motor.forward(speed=motorspeed)
    else:
        motor.backward(speed=motorspeed)
    time.sleep(abs(d_angle) * motor_time_scaling)

def arm_step(step_num):
    actuator_task = threading.Thread(target=actuator_step, args=[step_num])  # the threading library lets motors be controlled on 2 separate timers
    motor_task = threading.Thread(target=motor_step, args=[step_num])
    t = time.perf_counter()
    actuator_task.start()
    motor_task.start()
    actuator_task.join()
    motor_task.join()


def brush_movement():
    print()
    print("Brushing...")
    for step_num in range(1, calc.divs):
        arm_step(step_num)
        if stopped:
            return
    print()
    print("Movement complete!", end=" ")


def setup():  # user moves arm to initial position
    print()
    print("Set your arm angle and length with Mode and Stop buttons, then use Start to confirm.")
    start.wait_for_release()
    while not start.is_pressed:
        time.sleep(0.1)
        if mode.is_pressed:
            print("Raising...", end="\r")
            motor.forward(speed=motorspeed)
        elif stop.is_pressed:
            print("Lowering...", end="\r")
            motor.backward(speed=motorspeed)
        else:
            motor.stop()
            actuator.stop()
    print("Arm angle set!")
    start.wait_for_release()
    time.sleep(1)
    while not start.is_pressed:
        time.sleep(0.1)
        if mode.is_pressed:
            print("Extending...", end="\r")
            actuator.forward()
        elif stop.is_pressed:
            print("Retracting...", end="\r")
            actuator.backward()
        else:
            motor.stop()
            actuator.stop()
    print("Arm length set!")
    stop.when_pressed = stop_brushing
    mode.when_pressed = toggle_mode


def reset_position():
    motor.forward(speed=motorspeed)
    stop.wait_for_press(timeout=reset_motor_time)
    motor.stop()
    actuator.forward()
    stop.wait_for_press(timeout=reset_actuator_time)
    actuator.stop()

def main():
    global stopped, stop, mode
    calc.init_lookup_table()  # generate table of angles and lengths from parametric curve
    while True:
        print("Press Start to begin setting up.")
        start.wait_for_press()
        setup()
        stopped = False
        while stopped == False:
            brush_movement()
            if manual_mode:
                print("Continue? ", end="")
                while not start.is_pressed and not stopped:
                    time.sleep(0.5)
            else:
                print("Auto-reset: ", end="")
            if stopped:
                print("No")
            else:
                print("OK")
                reset_position()
        stop.close()
        mode.close()
        stop = Button(3)  # remove interrupt functions so that buttons can control the arm when rerunning setup
        mode = Button(4)
        print()
        print("Brush Buddy was stopped. ", end="")  # back to start


try:
    main()
except KeyboardInterrupt:
    print()
    print("off")
