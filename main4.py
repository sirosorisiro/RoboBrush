import calc
from gpiozero import Motor, Button
import time
import threading

# constants
actuator_time_scaling = 0.6  # <2
motor_time_scaling = 5
reset_motor_time = 1.5
reset_actuator_time = 5

# flags
manual_mode = True
stopped = False

motor = Motor(forward=20, backward=12)
actuator = Motor(forward=5, backward=6)
start = Button(2, bounce_time=0.05)
stop = Button(3, bounce_time=0.05)
mode = Button(4, bounce_time=0.05)
motor.value = 0.2
motor.stop()

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


def actuator_thread(step_events, done_event):
    for step_num in range(1, calc.divs):
        step_events[step_num].wait()  # wait for sync signal to start this step
        if stopped:
            return

        d_length = calc.table[step_num][2]
        print("Step (%d)/20: (%+.1f)mm " % (step_num, d_length), end="")

        if d_length > 0:
            actuator.forward()
        else:
            actuator.backward()
        time.sleep(actuator_time_scaling)
        actuator.stop()

        done_event[step_num].set()  # signal that actuator step is complete


def motor_thread(step_events, done_event):
    # Find the maximum absolute d_angle across all steps for normalization
    max_d_angle = max(abs(calc.table[s][3]) for s in range(1, calc.divs))
    if max_d_angle == 0:
        max_d_angle = 1  # avoid division by zero

    # Fixed step duration: use the max possible sleep time as the uniform duration
    step_duration = max_d_angle * motor_time_scaling

    for step_num in range(1, calc.divs):
        step_events[step_num].wait()  # wait for sync signal to start this step
        if stopped:
            motor.stop()
            return

        d_angle = calc.table[step_num][3]
        print("(%+.2f)rad" % d_angle, end="\r")

        # Scale motor.value by the ratio of this step's angle to the max angle
        speed = abs(d_angle) / max_d_angle
        speed = max(speed, 0.05)  # minimum speed to avoid stalling, adjust as needed

        if d_angle > 0:
            motor.value = speed
        elif d_angle < 0:
            motor.value = -speed
        else:
            motor.value = 0

        time.sleep(step_duration)
        motor.stop()

        done_event[step_num].set()  # signal that motor step is complete


def brush_movement():
    print()
    print("Brushing...")

    # Create sync events for each step
    step_events = {s: threading.Event() for s in range(1, calc.divs)}
    actuator_done = {s: threading.Event() for s in range(1, calc.divs)}
    motor_done = {s: threading.Event() for s in range(1, calc.divs)}

    act_thread = threading.Thread(target=actuator_thread, args=(step_events, actuator_done))
    mot_thread = threading.Thread(target=motor_thread, args=(step_events, motor_done))

    act_thread.start()
    mot_thread.start()

    for step_num in range(1, calc.divs):
        if stopped:
            # Unblock waiting threads so they can exit
            for s in range(step_num, calc.divs):
                step_events[s].set()
            break
        step_events[step_num].set()
        actuator_done[step_num].wait()
        motor_done[step_num].wait()

    act_thread.join()
    mot_thread.join()

    motor.stop()
    actuator.stop()

    if not stopped:
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
            motor.forward()
        elif stop.is_pressed:
            print("Lowering...", end="\r")
            motor.backward()
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
    motor.forward()
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
