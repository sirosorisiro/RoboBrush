from gpiozero import Motor
import time
motor = Motor(forward=12, backward=20)
while True:
    motor.forward()
