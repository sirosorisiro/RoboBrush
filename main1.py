from gpiozero import Motor
import time
import threading

motor = Motor(forward=12, backward=20)
actuator = Motor(forward=6, backward=5)
import calc

C = 1.0
length = 0.0
angle = 0.0
length_l = 0.0
angle_l = 0.0
table = [[0 for _ in range(4)] for _ in range(20)]

for i in range(20):
    buf = calc.calculate(i/20)
    length_l = length
    angle_l = angle
    length = buf["delta"]
    angle = buf["theta1"]
    table[i][0] = length
    table[i][1] = angle
    table[i][2] = length - length_l
    table[i][3] = angle - angle_l

def actuator_step(i):
    if table[i][2] > 0:
        print("a+" + str(table[i][2]/7))
        actuator.forward()
    else:
        print("a-" + str(table[i][2]/7))
        actuator.backward()
    time.sleep(abs(table[i][2]/7))
    actuator.stop()

def motor_step(i):                  # Fixed: added missing 'i' parameter
    if table[i][3] > 0:
        print("m+")
        motor.forward()
    else:
        print("m-")
        motor.backward()
    time.sleep(abs(table[i][3]) * C)
    motor.stop()                    # Fixed: was calling actuator.stop() by mistake

def time_step(i):
    # Create NEW threads every time the function is called
    thread1 = threading.Thread(target=actuator_step, args=(i,))
    thread2 = threading.Thread(target=motor_step, args=(i,))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()

for row in table:
    for element in row:
        print(element, end=" ")
    print()

for i in range(19):
    time_step(i+1)
