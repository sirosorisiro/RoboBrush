from gpiozero import Motor
import time
import threading

motor = Motor(forward=12, backward=20)
actuator = Motor(forward=6, backward=5)
import calc

C = 5
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

def setup():
    import sys
    import tty
    import termios
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        # Set terminal to raw mode so we can read single keypresses
        tty.setraw(sys.stdin.fileno())

        while True:
            key = sys.stdin.read(1).lower()

            if key == 'w':
                # Move cursor up and overwrite line
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                sys.stdout.write('Actuator forward...\r\n')
                sys.stdout.flush()
                actuator.forward()
                # Wait for key release (next keypress or small delay)
                while True:
                    tty.setraw(sys.stdin.fileno())
                    # Use select to check if another key is available
                    import select
                    ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if ready:
                        break
                    # Keep running motor while held
                actuator.stop()

            elif key == 's':
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                sys.stdout.write('Actuator backward...\r\n')
                sys.stdout.flush()
                actuator.backward()
                while True:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if ready:
                        break
                actuator.stop()

            elif key == 'a':
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                sys.stdout.write('Motor backward...\r\n')
                sys.stdout.flush()
                motor.backward()
                while True:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if ready:
                        break
                motor.stop()

            elif key == 'd':
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                sys.stdout.write('Motor forward...\r\n')
                sys.stdout.flush()
                motor.forward()
                while True:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if ready:
                        break
                motor.stop()

            elif key == 'q':
                actuator.stop()
                motor.stop()
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                sys.stdout.write('Exiting setup.\r\n')
                sys.stdout.flush()
                break

            else:
                # Any other key stops everything
                actuator.stop()
                motor.stop()

    finally:
        # Restore terminal settings no matter what
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    print("Setup complete. Motors in starting position.") 
def time_step(i):
    # Create NEW threads every time the function is called
    thread1 = threading.Thread(target=actuator_step, args=(i,))
    thread2 = threading.Thread(target=motor_step, args=(i,))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    time.sleep(0.5)

for row in table:
    for element in row:
        print(element, end=" ")
    print()
try:
    print("Setup")
    setup()
    for i in range(19):
        time_step(i+1)
except KeyboardInterrupt:
    print("Ending program")
