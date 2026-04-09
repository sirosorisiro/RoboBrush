import time
motor = Motor(forward=12, backward=20)
actuator = Motor(forward=5, backward=6)
import time
import calc
C = 1.0
length = 0.0
@@ -25,14 +24,20 @@

def time_step(i):
    if table[i][2] > 0:
        print("a+" + str(table[i][2]/7))
        actuator.forward()
    else:
        print("a-" + str(table[i][2]/7))
        actuator.backward()
    if table[i][3] > 0:
        print("m+")
        motor.forward()
    else:
        print("m-")
        motor.backward()
    time.sleep(table[i][3]*C)
    time.sleep(table[i][2]/7)
    actuator.stop()
    motor.stop()

for row in table:
    for element in row:
