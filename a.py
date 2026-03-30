from gpiozero import Motor
import time
motor = Motor(forward=12, backward=20)
act = Motor(forward=5, backward=6)
while True:
    motor.forward(speed=0.3)
    time.sleep(2)
    motor.backward(speed=0.3)
    time.sleep(2)
    act.forward()
    time.sleep(2)
    act.backward()
    time.sleep(2)
