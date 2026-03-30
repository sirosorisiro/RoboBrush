from gpiozero import Motor
import time
motor = Motor(forward=12, backward=20)
while True:
    motor.forward(speed=0.3)
    time.sleep(2)
    motor.backward(speed=0.3)
    time.sleep(2)
