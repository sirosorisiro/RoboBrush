from gpiozero import Motor
import time
motor = Motor(forward=12, backward=20)
actuator = Motor(forward=5, backward=6)
while True:
    # motor.forward(speed=0.3)
    # time.sleep(2)
    # motor.backward(speed=0.3)
    # time.sleep(2)
    actuator.forward()
    time.sleep(2)
    actuator.backward()
    time.sleep(2)
