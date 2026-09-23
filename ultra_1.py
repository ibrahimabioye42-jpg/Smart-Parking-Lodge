
from gpiozero import DistanceSensor, LED, Buzzer, AngularServo
from time import sleep, time


# ==================================================
# PARKING RATE
# ==================================================

RATE_PER_MINUTE = 1.00       # GH₵1.00 per minute


# ==================================================
# SLOT 1
# ==================================================

SLOT1_SENSOR = DistanceSensor(
    echo=17,
    trigger=18,
    max_distance=3
)

SLOT1_RED = LED(27)
SLOT1_GREEN = LED(22)
SLOT1_BUZZER = Buzzer(26)


# ==================================================
# SLOT 2
# ==================================================

SLOT2_SENSOR = DistanceSensor(
    echo=20,
    trigger=21,
    max_distance=3
)

SLOT2_RED = LED(23)
SLOT2_GREEN = LED(24)
SLOT2_BUZZER = Buzzer(19)


# ==================================================
# MAIN ENTRANCE GATE
# ==================================================

# Gate ultrasonic:
# TRIG = GPIO 6
# ECHO = GPIO 13

GATE_SENSOR = DistanceSensor(
    echo=13,
    trigger=6,
    max_distance=3
)


# Servo signal:
# GPIO 5

GATE_SERVO = AngularServo(
    5,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)


# ==================================================
# GATE SERVO POSITIONS
# ==================================================

GATE_OPEN_ANGLE = 100
GATE_CLOSED_ANGLE = 180


# ==================================================
# DISTANCE SETTINGS
# ==================================================

TOO_CLOSE_DISTANCE = 5
CLOSE_DISTANCE = 15
FAR_DISTANCE = 70

# Car within 70 cm opens gate
GATE_DETECT_DISTANCE = 70


# ==================================================
# PARKING TIMER VARIABLES
# ==================================================

slot1_start_time = None
slot2_start_time = None

slot1_car_present = False
slot2_car_present = False


# ==================================================
# SLOT 1
# ==================================================

def update_slot1():

    global slot1_start_time
    global slot1_car_present

    distance = SLOT1_SENSOR.distance * 100

    # ----------------------------------------------
    # TOO CLOSE
    # ----------------------------------------------

    if distance < TOO_CLOSE_DISTANCE:

        SLOT1_RED.toggle()
        SLOT1_GREEN.off()
        SLOT1_BUZZER.toggle()

        status = "TOO CLOSE - WARNING"

    # ----------------------------------------------
    # CLOSE
    # ----------------------------------------------

    elif distance < CLOSE_DISTANCE:

        SLOT1_RED.on()
        SLOT1_GREEN.off()
        SLOT1_BUZZER.off()

        status = "CLOSE"

    # ----------------------------------------------
    # CAR DETECTED
    # ----------------------------------------------

    elif distance <= FAR_DISTANCE:

        SLOT1_RED.off()
        SLOT1_GREEN.on()
        SLOT1_BUZZER.off()

        status = "CAR_DETECTED"

    # ----------------------------------------------
    # FREE
    # ----------------------------------------------

    else:

        SLOT1_RED.off()
        SLOT1_GREEN.off()
        SLOT1_BUZZER.off()

        status = "FREE_SLOT"


    # ==================================================
    # START PARKING TIMER
    # ==================================================

    if distance <= FAR_DISTANCE and not slot1_car_present:

        slot1_start_time = time()
        slot1_car_present = True

        print(">>> SLOT 1 TIMER STARTED")


    # ==================================================
    # STOP PARKING TIMER
    # ==================================================

    elif distance > FAR_DISTANCE and slot1_car_present:

        end_time = time()

        elapsed_seconds = end_time - slot1_start_time
        elapsed_minutes = elapsed_seconds / 60

        amount = elapsed_minutes * RATE_PER_MINUTE

        print()
        print("================================")
        print("        SLOT 1 PAYMENT")
        print("================================")
        print(f"Time parked : {elapsed_minutes:.2f} minutes")
        print(f"Amount      : GH₵{amount:.2f}")
        print("================================")
        print()

        slot1_start_time = None
        slot1_car_present = False


    print(f"Slot 1: {distance:.2f} cm - {status}")


# ==================================================
# SLOT 2
# ==================================================

def update_slot2():

    global slot2_start_time
    global slot2_car_present

    distance = SLOT2_SENSOR.distance * 100

    # ----------------------------------------------
    # TOO CLOSE
    # ----------------------------------------------

    if distance < TOO_CLOSE_DISTANCE:

        SLOT2_RED.toggle()
        SLOT2_GREEN.off()
        SLOT2_BUZZER.toggle()

        status = "TOO CLOSE - WARNING"

    # ----------------------------------------------
    # CLOSE
    # ----------------------------------------------

    elif distance < CLOSE_DISTANCE:

        SLOT2_RED.on()
        SLOT2_GREEN.off()
        SLOT2_BUZZER.off()

        status = "CLOSE"

    # ----------------------------------------------
    # CAR DETECTED
    # ----------------------------------------------

    elif distance <= FAR_DISTANCE:

        SLOT2_RED.off()
        SLOT2_GREEN.on()
        SLOT2_BUZZER.off()

        status = "CAR_DETECTED"

    # ----------------------------------------------
    # FREE
    # ----------------------------------------------

    else:

        SLOT2_RED.off()
        SLOT2_GREEN.off()
        SLOT2_BUZZER.off()

        status = "FREE_SLOT"


    # ==================================================
    # START PARKING TIMER
    # ==================================================

    if distance <= FAR_DISTANCE and not slot2_car_present:

        slot2_start_time = time()
        slot2_car_present = True

        print(">>> SLOT 2 TIMER STARTED")


    # ==================================================
    # STOP PARKING TIMER
    # ==================================================

    elif distance > FAR_DISTANCE and slot2_car_present:

        end_time = time()

        elapsed_seconds = end_time - slot2_start_time
        elapsed_minutes = elapsed_seconds / 60

        amount = elapsed_minutes * RATE_PER_MINUTE

        print()
        print("================================")
        print("        SLOT 2 PAYMENT")
        print("================================")
        print(f"Time parked : {elapsed_minutes:.2f} minutes")
        print(f"Amount      : GH₵{amount:.2f}")
        print("================================")
        print()

        slot2_start_time = None
        slot2_car_present = False


    print(f"Slot 2: {distance:.2f} cm - {status}")


# ==================================================
# MAIN ENTRANCE GATE
# ==================================================

def update_gate():

    distance = GATE_SENSOR.distance * 100

    # ----------------------------------------------
    # CAR DETECTED
    # ----------------------------------------------

    if distance <= GATE_DETECT_DISTANCE:

        GATE_SERVO.angle = GATE_OPEN_ANGLE

        print(
            f"MAIN GATE: CAR DETECTED "
            f"({distance:.2f} cm) - OPEN"
        )

    # ----------------------------------------------
    # NO CAR
    # ----------------------------------------------

    else:

        GATE_SERVO.angle = GATE_CLOSED_ANGLE

        print(
            f"MAIN GATE: NO CAR "
            f"({distance:.2f} cm) - CLOSED"
        )


# ==================================================
# START SYSTEM
# ==================================================

print()
print("==============================================")
print("          SMART PARKING SYSTEM")
print("==============================================")
print()

print("MAIN GATE")
print("Ultrasonic: Trigger GPIO 6")
print("Ultrasonic: Echo GPIO 13")
print("Servo: GPIO 5")
print(f"Open angle: {GATE_OPEN_ANGLE} degrees")
print(f"Closed angle: {GATE_CLOSED_ANGLE} degrees")
print()

print("SLOT 1")
print("Sensor: Trigger GPIO 18 / Echo GPIO 17")
print()

print("SLOT 2")
print("Sensor: Trigger GPIO 21 / Echo GPIO 20")
print()

print(f"Parking rate: GH₵{RATE_PER_MINUTE:.2f} per minute")
print()

print("Press Ctrl+C to stop.")
print()


# ==================================================
# INITIAL GATE POSITION
# ==================================================

GATE_SERVO.angle = GATE_CLOSED_ANGLE

print("Main gate initialized: CLOSED")


# ==================================================
# MAIN LOOP
# ==================================================

try:

    while True:

        # Check parking slots
        update_slot1()

        update_slot2()

        # Check main entrance
        update_gate()

        print("----------------------------------------------")

        sleep(0.25)


except KeyboardInterrupt:

    print()
    print("System stopped.")


finally:

    # Turn OFF Slot 1
    SLOT1_RED.off()
    SLOT1_GREEN.off()
    SLOT1_BUZZER.off()

    # Turn OFF Slot 2
    SLOT2_RED.off()
    SLOT2_GREEN.off()
    SLOT2_BUZZER.off()

    # Close main gate
    GATE_SERVO.angle = GATE_CLOSED_ANGLE

    print("All LEDs and buzzers OFF.")
    print("Main gate CLOSED.")

