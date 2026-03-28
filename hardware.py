# hardware.py

from gpiozero import Motor, Servo, Buzzer, Button
import time


class Hardware:

    def __init__(self):

        # -----------------
        # Motors
        # -----------------
        self.dc_motor = Motor(forward=12, backward=20)
        self.actuator_motor = Motor(forward=5, backward=6)

        # -----------------
        # Servo
        # -----------------
        self.servo = Servo(
            8,
            min_pulse_width=0.75/1000,
            max_pulse_width=2.25/1000
        )



        # -----------------
        # Buttons
        # -----------------
        self.btn_pancake = Button(19, pull_up=True)
        self.btn_eggs = Button(21, pull_up=True)
        self.btn_steak = Button(13, pull_up=True)

    # -----------------
    # Motor Control
    # -----------------

    # Motor Control

    def dc_raise(self, t):
        self.dc_motor.backward()
        time.sleep(t)
        self.dc_motor.stop()

    def dc_lower(self, t):
        self.dc_motor.forward()
        time.sleep(t)
        self.dc_motor.stop()

    def actuator_extend(self, t):
        self.actuator_motor.forward()
        time.sleep(t)
        self.actuator_motor.stop()

    def actuator_retract(self, t):
        self.actuator_motor.backward()
        time.sleep(t)
        self.actuator_motor.stop()


    # -----------------
    # Servo
    # -----------------

    def flip(self):
        self.servo.value = -1
        time.sleep(0.6)
        self.servo.value = 1
        time.sleep(0.6)
        self.servo.value = None  # prevent jitter

    # -----------------
    # Buzzer
    # -----------------

    def beep(self, times=1, duration=0.2):
        for _ in range(times):
            self.buzzer.on()
            time.sleep(duration)
            self.buzzer.off()
            time.sleep(duration)
