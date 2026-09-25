
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
# MAIN ENTRANCE / EXIT GATE
# ==================================================

# Gate ultrasonic:
# TRIG = GPIO 6
# ECHO = GPIO 13

GATE_SENSOR = DistanceSensor(
    echo=13,
    trigger=6,
    max_distance=3
)


# ==================================================
# SG90 SERVO
# ==================================================

# SG90 signal wire -> GPIO 5

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

TOO_CLOSE_DISTANCE = 4
CLOSE_DISTANCE = 15
FAR_DISTANCE = 25

# Main gate vehicle detection
GATE_DETECT_DISTANCE = 40


# ==================================================
# GATE CLOSE DELAY
# ==================================================

# Time the gate remains open after the vehicle
# clears the main gate ultrasonic sensor.

GATE_CLOSE_DELAY = 120       # 2 minutes


# ==================================================
# PARKING TIMER VARIABLES
# ==================================================

slot1_start_time = None
slot2_start_time = None

slot1_car_present = False
slot2_car_present = False


# ==================================================
# SLOT STATES
# ==================================================

slot1_state = "UNKNOWN"
slot2_state = "UNKNOWN"

previous_slot1_state = "UNKNOWN"
previous_slot2_state = "UNKNOWN"


# ==================================================
# EXIT DETECTION
# ==================================================

# These become True after a vehicle has been detected
# in a slot.
#
# This prevents a slot that is already FREE at startup
# from opening the gate.

slot1_was_occupied = False
slot2_was_occupied = False


# ==================================================
# MAIN GATE STATE
# ==================================================

gate_is_open = False

# Time when vehicle leaves the main gate sensor
gate_close_start_time = None


# ==================================================
# OPEN MAIN GATE
# ==================================================

def open_gate():

    global gate_is_open
    global gate_close_start_time

    # Cancel any existing close countdown

    gate_close_start_time = None


    # Only send an OPEN command if gate is closed

    if not gate_is_open:

        print()
        print("================================")
        print("       OPEN GATE COMMAND")
        print("================================")

        GATE_SERVO.angle = GATE_OPEN_ANGLE

        gate_is_open = True

        print(
            f"SG90 moved to "
            f"{GATE_OPEN_ANGLE} degrees"
        )

        print("MAIN GATE: OPEN")
        print("================================")
        print()


# ==================================================
# CLOSE MAIN GATE
# ==================================================

def close_gate():

    global gate_is_open
    global gate_close_start_time

    # Only send CLOSE command if gate is open

    if gate_is_open:

        print()
        print("================================")
        print("       CLOSE GATE COMMAND")
        print("================================")

        GATE_SERVO.angle = GATE_CLOSED_ANGLE

        gate_is_open = False

        gate_close_start_time = None

        print(
            f"SG90 moved to "
            f"{GATE_CLOSED_ANGLE} degrees"
        )

        print("MAIN GATE: CLOSED")
        print("================================")
        print()


# ==================================================
# SLOT 1
# ==================================================

def update_slot1():

    global slot1_start_time
    global slot1_car_present
    global slot1_state
    global previous_slot1_state
    global slot1_was_occupied

    distance = SLOT1_SENSOR.distance * 100


    # ==================================================
    # ORIGINAL LOGIC
    # TOO CLOSE
    # ==================================================

    if distance < TOO_CLOSE_DISTANCE:

        SLOT1_RED.toggle()

        SLOT1_GREEN.off()

        SLOT1_BUZZER.toggle()

        status = "TOO CLOSE - WARNING"


    # ==================================================
    # ORIGINAL LOGIC
    # 4 cm - <15 cm
    # PARKED
    # ==================================================

    elif distance < CLOSE_DISTANCE:

        SLOT1_RED.on()

        SLOT1_GREEN.off()

        SLOT1_BUZZER.off()

        status = "PARKED"


    # ==================================================
    # ORIGINAL LOGIC
    # 15 cm - 25 cm
    # CAR DETECTED
    # ==================================================

    elif distance <= FAR_DISTANCE:

        SLOT1_RED.off()

        SLOT1_GREEN.on()

        SLOT1_BUZZER.off()

        status = "CAR_DETECTED"


    # ==================================================
    # ORIGINAL LOGIC
    # >25 cm
    # FREE
    # ==================================================

    else:

        SLOT1_RED.off()

        SLOT1_GREEN.off()

        SLOT1_BUZZER.off()

        status = "FREE_SLOT"


    # ==================================================
    # SAVE STATE
    # ==================================================

    previous_slot1_state = slot1_state

    slot1_state = status


    # ==================================================
    # START PARKING TIMER
    # ==================================================

    if distance <= FAR_DISTANCE and not slot1_car_present:

        slot1_start_time = time()

        slot1_car_present = True

        slot1_was_occupied = True

        print()
        print(">>> SLOT 1 TIMER STARTED")
        print()


    # ==================================================
    # STOP PARKING TIMER
    # CAR HAS LEFT
    # ==================================================

    elif distance > FAR_DISTANCE and slot1_car_present:

        end_time = time()

        elapsed_seconds = (
            end_time - slot1_start_time
        )

        elapsed_minutes = (
            elapsed_seconds / 60
        )

        amount = (
            elapsed_minutes *
            RATE_PER_MINUTE
        )


        # ==================================================
        # PAYMENT
        # ==================================================

        print()
        print("================================")
        print("        SLOT 1 PAYMENT")
        print("================================")
        print(
            f"Time parked : "
            f"{elapsed_minutes:.2f} minutes"
        )
        print(
            f"Rate        : "
            f"GH₵{RATE_PER_MINUTE:.2f} / minute"
        )
        print(
            f"Amount      : "
            f"GH₵{amount:.2f}"
        )
        print("================================")
        print()


        slot1_start_time = None

        slot1_car_present = False


        # ==================================================
        # EXIT GATE COMMAND
        # ==================================================

        if slot1_was_occupied:

            print(">>> SLOT 1 IS FREE")

            print(">>> EXIT VEHICLE DETECTED")

            print(">>> OPENING MAIN GATE")

            open_gate()

            slot1_was_occupied = False


    # ==================================================
    # DISPLAY SLOT
    # ==================================================

    print(
        f"Slot 1: "
        f"{distance:.2f} cm - "
        f"{status}"
    )


# ==================================================
# SLOT 2
# ==================================================

def update_slot2():

    global slot2_start_time
    global slot2_car_present
    global slot2_state
    global previous_slot2_state
    global slot2_was_occupied

    distance = SLOT2_SENSOR.distance * 100


    # ==================================================
    # ORIGINAL LOGIC
    # TOO CLOSE
    # ==================================================

    if distance < TOO_CLOSE_DISTANCE:

        SLOT2_RED.toggle()

        SLOT2_GREEN.off()

        SLOT2_BUZZER.toggle()

        status = "TOO CLOSE - WARNING"


    # ==================================================
    # ORIGINAL LOGIC
    # 4 cm - <15 cm
    # PARKED
    # ==================================================

    elif distance < CLOSE_DISTANCE:

        SLOT2_RED.on()

        SLOT2_GREEN.off()

        SLOT2_BUZZER.off()

        status = "PARKED"


    # ==================================================
    # ORIGINAL LOGIC
    # 15 cm - 25 cm
    # CAR DETECTED
    # ==================================================

    elif distance <= FAR_DISTANCE:

        SLOT2_RED.off()

        SLOT2_GREEN.on()

        SLOT2_BUZZER.off()

        status = "CAR_DETECTED"


    # ==================================================
    # ORIGINAL LOGIC
    # >25 cm
    # FREE
    # ==================================================

    else:

        SLOT2_RED.off()

        SLOT2_GREEN.off()

        SLOT2_BUZZER.off()

        status = "FREE_SLOT"


    # ==================================================
    # SAVE STATE
    # ==================================================

    previous_slot2_state = slot2_state

    slot2_state = status


    # ==================================================
    # START PARKING TIMER
    # ==================================================

    if distance <= FAR_DISTANCE and not slot2_car_present:

        slot2_start_time = time()

        slot2_car_present = True

        slot2_was_occupied = True

        print()
        print(">>> SLOT 2 TIMER STARTED")
        print()


    # ==================================================
    # STOP PARKING TIMER
    # CAR HAS LEFT
    # ==================================================

    elif distance > FAR_DISTANCE and slot2_car_present:

        end_time = time()

        elapsed_seconds = (
            end_time - slot2_start_time
        )

        elapsed_minutes = (
            elapsed_seconds / 60
        )

        amount = (
            elapsed_minutes *
            RATE_PER_MINUTE
        )


        # ==================================================
        # PAYMENT
        # ==================================================

        print()
        print("================================")
        print("        SLOT 2 PAYMENT")
        print("================================")
        print(
            f"Time parked : "
            f"{elapsed_minutes:.2f} minutes"
        )
        print(
            f"Rate        : "
            f"GH₵{RATE_PER_MINUTE:.2f} / minute"
        )
        print(
            f"Amount      : "
            f"GH₵{amount:.2f}"
        )
        print("================================")
        print()


        slot2_start_time = None

        slot2_car_present = False


        # ==================================================
        # EXIT GATE COMMAND
        # ==================================================

        if slot2_was_occupied:

            print(">>> SLOT 2 IS FREE")

            print(">>> EXIT VEHICLE DETECTED")

            print(">>> OPENING MAIN GATE")

            open_gate()

            slot2_was_occupied = False


    # ==================================================
    # DISPLAY SLOT
    # ==================================================

    print(
        f"Slot 2: "
        f"{distance:.2f} cm - "
        f"{status}"
    )


# ==================================================
# MAIN ENTRANCE / EXIT GATE
# ==================================================

def update_gate():

    global gate_close_start_time

    distance = GATE_SENSOR.distance * 100


    # ==================================================
    # ENTRY
    # ==================================================
    #
    # Main gate ultrasonic detects a vehicle.
    #
    # This is an OPEN command.
    #

    if distance <= GATE_DETECT_DISTANCE:

        print(
            f"MAIN GATE: "
            f"CAR DETECTED "
            f"({distance:.2f} cm)"
        )

        open_gate()

        return


    # ==================================================
    # VEHICLE HAS LEFT THE MAIN GATE SENSOR
    # ==================================================

    if gate_is_open:

        # ----------------------------------------------
        # START CLOSE COUNTDOWN
        # ----------------------------------------------

        if gate_close_start_time is None:

            gate_close_start_time = time()

            print()
            print(">>> VEHICLE CLEARED MAIN GATE")

            print(
                f">>> CLOSE TIMER STARTED: "
                f"{GATE_CLOSE_DELAY} seconds"
            )

            print()


        # ----------------------------------------------
        # CHECK CLOSE COUNTDOWN
        # ----------------------------------------------

        else:

            elapsed = (
                time() -
                gate_close_start_time
            )

            remaining = (
                GATE_CLOSE_DELAY -
                elapsed
            )


            # ------------------------------------------
            # WAIT
            # ------------------------------------------

            if remaining > 0:

                print(
                    f"MAIN GATE OPEN | "
                    f"Closing in "
                    f"{remaining:.0f} seconds"
                )


            # ------------------------------------------
            # CLOSE
            # ------------------------------------------

            else:

                close_gate()


# ==================================================
# SYSTEM START
# ==================================================

print()
print("==============================================")
print("          SMART PARKING SYSTEM")
print("==============================================")
print()

print("MAIN ENTRANCE / EXIT GATE")
print("----------------------------------------------")
print("Ultrasonic Trigger : GPIO 6")
print("Ultrasonic Echo    : GPIO 13")
print("SG90 Servo Signal  : GPIO 5")
print(
    f"Open angle         : "
    f"{GATE_OPEN_ANGLE} degrees"
)
print(
    f"Closed angle       : "
    f"{GATE_CLOSED_ANGLE} degrees"
)
print(
    f"Close delay        : "
    f"{GATE_CLOSE_DELAY} seconds"
)
print()

print("SLOT 1")
print("----------------------------------------------")
print("Trigger : GPIO 18")
print("Echo    : GPIO 17")
print("Red     : GPIO 27")
print("Green   : GPIO 22")
print("Buzzer  : GPIO 26")
print()

print("SLOT 2")
print("----------------------------------------------")
print("Trigger : GPIO 21")
print("Echo    : GPIO 20")
print("Red     : GPIO 23")
print("Green   : GPIO 24")
print("Buzzer  : GPIO 19")
print()

print(
    f"Parking rate: "
    f"GH₵{RATE_PER_MINUTE:.2f} per minute"
)

print()

# ==================================================
# IMPORTANT
# ==================================================
#
# DO NOT SET THE SERVO ANGLE HERE.
#
# The SG90 remains still until open_gate() or
# close_gate() sends a command.
#
# ==================================================

print("SG90 servo waiting for command...")
print("Press Ctrl+C to stop.")
print()


# ==================================================
# MAIN LOOP
# ==================================================

try:

    while True:

        # ------------------------------------------
        # CHECK SLOT 1
        # ------------------------------------------

        update_slot1()


        # ------------------------------------------
        # CHECK SLOT 2
        # ------------------------------------------

        update_slot2()


        # ------------------------------------------
        # CHECK MAIN GATE
        # ------------------------------------------

        update_gate()


        print("----------------------------------------------")

        sleep(0.25)


# ==================================================
# STOP SYSTEM
# ==================================================

except KeyboardInterrupt:

    print()
    print("System stopped.")


# ==================================================
# CLEANUP
# ==================================================

finally:

    # Turn OFF Slot 1

    SLOT1_RED.off()
    SLOT1_GREEN.off()
    SLOT1_BUZZER.off()


    # Turn OFF Slot 2

    SLOT2_RED.off()
    SLOT2_GREEN.off()
    SLOT2_BUZZER.off()


    # IMPORTANT:
    #
    # No servo command here.
    #
    # The SG90 remains at its current position.
    #

    print("All LEDs and buzzers OFF.")
    print("SG90 servo position unchanged.")
    print("System safely stopped.")

