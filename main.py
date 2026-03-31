from gpiozero import Motor
import time
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
    # print("length", length, "angle", angle, "diff", length-length_l, angle-angle_l)
    table[i][0] =  length
    table[i][1] = angle
    table[i][2] = length-length_l
    table[i][3] = angle-angle_l

def actuator_step(i):
    if table[i][2] > 0:
        print("a+" + str(table[i][2]/7))
        actuator.forward()
    else:
        print("a-" + str(table[i][2]/7))
        actuator.backward()
    time.sleep(abs(table[i][2]/7))
    actuator.stop()

def run_motor2():
    if table[i][3] > 0:
        print("m+")
        motor.forward()
    else:
        print("m-")
        motor.backward()
    time.sleep(abs(table[i][3]) * C)
    actuator.stop()

# Create threads
thread1 = threading.Thread(target=run_motor1)
thread2 = threading.Thread(target=run_motor2)

# Start threads


# Wait for both to finish

def time_step(i):
    thread1.start()
    thread2.start()
    time.sleep(1)
    thread1.join()
    thread2.join()
    
for row in table:
    for element in row:
        print(element, end=" ") # 'end=" "' keeps elements on the same line
    print() # Adds a newline after each row is finished
    

for i in range(19):
    time_step(i+1)
