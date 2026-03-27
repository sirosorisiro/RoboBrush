from gpiozero import DistanceSensor
ultrasonic = DistanceSensor(echo=27, trigger=17)
while True:
    print(ultrasonic.distance)
