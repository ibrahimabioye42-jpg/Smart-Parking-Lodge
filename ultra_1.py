
from gpiozero import DistanceSensor, LED, Buzzer, AngularServo
from time import sleep, time
import os


# ==========================================================
#                  SMART PARKING SYSTEM
# ==========================================================
#
# SLOT 1
# Trigger -> GPIO 18
# Echo    -> GPIO 17
# Red     -> GPIO 27
# Green   -> GPIO 22
# Buzzer  -> GPIO 26
#
# SLOT 2
# Trigger -> GPIO 21
# Echo    -> GPIO 20
# Red     -> GPIO 23
# Green   -> GPIO 24
# Buzzer  -> GPIO 19
#
# MAIN GATE
# Trigger -> GPIO 6
# Echo    -> GPIO 13
# Servo   -> GPIO 5
#
# ==========================================================


# ==========================================================
# PARKING RATE
# ==========================================================

RATE_PER_MINUTE = 1.00       # GH₵1.00 per minute


# ==========================================================
# PARKING SLOT DISTANCES
# ==========================================================

TOO_CLOSE_DISTANCE = 4       # Below 4 cm
CLOSE_DISTANCE = 15          # 4 - <15 cm
FAR_DISTANCE = 25            # 15 - 25 cm


# ==========================================================
# MAIN GATE DETECTION
# ==========================================================

GATE_DETECT_DISTANCE = 40   # Vehicle detected at <= 40 cm


# ==========================================================
# MAIN GATE OPEN TIME
# ==========================================================

GATE_CLOSE_DELAY = 30       # Gate closes 30 seconds after opening


# ==========================================================
# RED LED BLINK SPEED
# ==========================================================

BLINK_INTERVAL = 0.30


# ==========================================================
# SLOT 1 SENSOR
# ==========================================================

SLOT1_SENSOR = DistanceSensor(
    echo=17,
    trigger=18,
    max_distance=3
)


# ==========================================================
# SLOT 1 OUTPUTS
# ==========================================================

SLOT1_RED = LED(27)
SLOT1_GREEN = LED(22)
SLOT1_BUZZER = Buzzer(26)


# ==========================================================
# SLOT 2 SENSOR
# ==========================================================

SLOT2_SENSOR = DistanceSensor(
    echo=20,
    trigger=21,
    max_distance=3
)


# ==========================================================
# SLOT 2 OUTPUTS
# ==========================================================

SLOT2_RED = LED(23)
SLOT2_GREEN = LED(24)
SLOT2_BUZZER = Buzzer(19)


# ==========================================================
# MAIN GATE SENSOR
# ==========================================================

GATE_SENSOR = DistanceSensor(
    echo=13,
    trigger=6,
    max_distance=3
)


# ==========================================================
# SG90 SERVO
# ==========================================================

GATE_SERVO = AngularServo(
    5,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)


# ==========================================================
# SERVO POSITIONS
# ==========================================================

GATE_OPEN_ANGLE = 100
GATE_CLOSED_ANGLE = 180


# ==========================================================
# SLOT 1 VARIABLES
# ==========================================================

slot1_distance = 0

slot1_state = "FREE"

slot1_car_present = False

slot1_start_time = None

slot1_was_occupied = False


# ==========================================================
# SLOT 2 VARIABLES
# ==========================================================

slot2_distance = 0

slot2_state = "FREE"

slot2_car_present = False

slot2_start_time = None

slot2_was_occupied = False


# ==========================================================
# MAIN GATE VARIABLES
# ==========================================================

gate_distance = 0

gate_is_open = False

# Time when the gate opened
gate_open_time = None


# ==========================================================
# BLINK VARIABLES
# ==========================================================

last_blink_time = 0

blink_state = False


# ==========================================================
# CLEAR TERMINAL
# ==========================================================

def clear_screen():

    os.system("clear")


# ==========================================================
# OPEN MAIN GATE
# ==========================================================

def open_gate():

    global gate_is_open
    global gate_open_time

    # ------------------------------------------------------
    # Only open if currently closed
    # ------------------------------------------------------

    if not gate_is_open:

        GATE_SERVO.angle = GATE_OPEN_ANGLE

        gate_is_open = True

        # Start 30-second timer immediately
        gate_open_time = time()


# ==========================================================
# CLOSE MAIN GATE
# ==========================================================

def close_gate():

    global gate_is_open
    global gate_open_time

    if gate_is_open:

        GATE_SERVO.angle = GATE_CLOSED_ANGLE

        gate_is_open = False

        gate_open_time = None


# ==========================================================
# NUMBER OF FREE SLOTS
# ==========================================================

def available_slot_count():

    count = 0

    if not slot1_car_present:
        count += 1

    if not slot2_car_present:
        count += 1

    return count


# ==========================================================
# PARKING TIME
# ==========================================================

def get_parking_minutes(start_time):

    if start_time is None:
        return 0

    elapsed_seconds = time() - start_time

    return elapsed_seconds / 60


# ==========================================================
# CURRENT PARKING CHARGE
# ==========================================================

def get_current_charge(start_time):

    minutes = get_parking_minutes(start_time)

    return minutes * RATE_PER_MINUTE


# ==========================================================
# UPDATE SLOT 1
# ==========================================================

def update_slot1():

    global slot1_distance
    global slot1_state
    global slot1_car_present
    global slot1_start_time
    global slot1_was_occupied

    # Read sensor
    distance = SLOT1_SENSOR.distance * 100

    slot1_distance = distance


    # ======================================================
    # TOO CLOSE
    # ======================================================

    if distance < TOO_CLOSE_DISTANCE:

        slot1_state = "TOO CLOSE"

        # Green OFF
        SLOT1_GREEN.off()

        # Buzzer ON
        SLOT1_BUZZER.on()


    # ======================================================
    # PARKED
    # ======================================================

    elif distance < CLOSE_DISTANCE:

        slot1_state = "PARKED"

        # Red ON
        SLOT1_RED.on()

        # Green OFF
        SLOT1_GREEN.off()

        # Buzzer OFF
        SLOT1_BUZZER.off()


    # ======================================================
    # CAR DETECTED
    # ======================================================

    elif distance <= FAR_DISTANCE:

        slot1_state = "CAR DETECTED"

        # Red OFF
        SLOT1_RED.off()

        # Green ON
        SLOT1_GREEN.on()

        # Buzzer OFF
        SLOT1_BUZZER.off()


    # ======================================================
    # FREE
    # ======================================================

    else:

        slot1_state = "FREE"

        SLOT1_RED.off()

        SLOT1_GREEN.off()

        SLOT1_BUZZER.off()


    # ======================================================
    # VEHICLE ENTERED SLOT
    # ======================================================

    if distance <= FAR_DISTANCE:

        if not slot1_car_present:

            slot1_start_time = time()

            slot1_car_present = True

            slot1_was_occupied = True


    # ======================================================
    # VEHICLE LEFT SLOT
    # ======================================================

    elif distance > FAR_DISTANCE:

        if slot1_car_present:

            # ----------------------------------------------
            # CALCULATE PARKING TIME
            # ----------------------------------------------

            elapsed_seconds = (
                time() -
                slot1_start_time
            )

            elapsed_minutes = (
                elapsed_seconds / 60
            )


            # ----------------------------------------------
            # CALCULATE PAYMENT
            # ----------------------------------------------

            amount = (
                elapsed_minutes *
                RATE_PER_MINUTE
            )


            # ----------------------------------------------
            # PAYMENT MESSAGE
            # ----------------------------------------------

            print()

            print("=" * 55)

            print("                  SLOT 1 PAYMENT")

            print("=" * 55)

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

            print("=" * 55)

            print()


            # ----------------------------------------------
            # RESET SLOT
            # ----------------------------------------------

            slot1_start_time = None

            slot1_car_present = False


            # ----------------------------------------------
            # OPEN GATE FOR EXITING VEHICLE
            # ----------------------------------------------

            if slot1_was_occupied:

                open_gate()

                slot1_was_occupied = False


# ==========================================================
# UPDATE SLOT 2
# ==========================================================

def update_slot2():

    global slot2_distance
    global slot2_state
    global slot2_car_present
    global slot2_start_time
    global slot2_was_occupied

    # Read sensor
    distance = SLOT2_SENSOR.distance * 100

    slot2_distance = distance


    # ======================================================
    # TOO CLOSE
    # ======================================================

    if distance < TOO_CLOSE_DISTANCE:

        slot2_state = "TOO CLOSE"

        SLOT2_GREEN.off()

        SLOT2_BUZZER.on()


    # ======================================================
    # PARKED
    # ======================================================

    elif distance < CLOSE_DISTANCE:

        slot2_state = "PARKED"

        SLOT2_RED.on()

        SLOT2_GREEN.off()

        SLOT2_BUZZER.off()


    # ======================================================
    # CAR DETECTED
    # ======================================================

    elif distance <= FAR_DISTANCE:

        slot2_state = "CAR DETECTED"

        SLOT2_RED.off()

        SLOT2_GREEN.on()

        SLOT2_BUZZER.off()


    # ======================================================
    # FREE
    # ======================================================

    else:

        slot2_state = "FREE"

        SLOT2_RED.off()

        SLOT2_GREEN.off()

        SLOT2_BUZZER.off()


    # ======================================================
    # VEHICLE ENTERED SLOT
    # ======================================================

    if distance <= FAR_DISTANCE:

        if not slot2_car_present:

            slot2_start_time = time()

            slot2_car_present = True

            slot2_was_occupied = True


    # ======================================================
    # VEHICLE LEFT SLOT
    # ======================================================

    elif distance > FAR_DISTANCE:

        if slot2_car_present:

            # ----------------------------------------------
            # CALCULATE PARKING TIME
            # ----------------------------------------------

            elapsed_seconds = (
                time() -
                slot2_start_time
            )

            elapsed_minutes = (
                elapsed_seconds / 60
            )


            # ----------------------------------------------
            # CALCULATE PAYMENT
            # ----------------------------------------------

            amount = (
                elapsed_minutes *
                RATE_PER_MINUTE
            )


            # ----------------------------------------------
            # PAYMENT MESSAGE
            # ----------------------------------------------

            print()

            print("=" * 55)

            print("                  SLOT 2 PAYMENT")

            print("=" * 55)

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

            print("=" * 55)

            print()


            # ----------------------------------------------
            # RESET SLOT
            # ----------------------------------------------

            slot2_start_time = None

            slot2_car_present = False


            # ----------------------------------------------
            # OPEN GATE FOR EXITING VEHICLE
            # ----------------------------------------------

            if slot2_was_occupied:

                open_gate()

                slot2_was_occupied = False


# ==========================================================
# UPDATE MAIN GATE
# ==========================================================

def update_gate():

    global gate_distance
    global gate_open_time

    # ------------------------------------------------------
    # READ MAIN GATE SENSOR
    # ------------------------------------------------------

    distance = GATE_SENSOR.distance * 100

    gate_distance = distance


    # ======================================================
    # CAR DETECTED AT MAIN GATE
    # ======================================================

    if distance <= GATE_DETECT_DISTANCE:

        # Open immediately
        open_gate()


    # ======================================================
    # CHECK 30-SECOND TIMER
    # ======================================================

    if gate_is_open:

        # Safety check
        if gate_open_time is None:

            gate_open_time = time()


        # Calculate how long gate has been open
        elapsed = (
            time() -
            gate_open_time
        )


        # --------------------------------------------------
        # CLOSE AFTER 30 SECONDS
        # --------------------------------------------------

        if elapsed >= GATE_CLOSE_DELAY:

            close_gate()


# ==========================================================
# UPDATE BLINKING WARNING LIGHTS
# ==========================================================

def update_warning_lights():

    global last_blink_time
    global blink_state

    current_time = time()


    # Check blink interval
    if (
        current_time -
        last_blink_time
        >= BLINK_INTERVAL
    ):

        last_blink_time = current_time

        blink_state = not blink_state


        # ==================================================
        # SLOT 1
        # ==================================================

        if slot1_state == "TOO CLOSE":

            if blink_state:

                SLOT1_RED.on()

            else:

                SLOT1_RED.off()

        elif slot1_state == "PARKED":

            SLOT1_RED.on()

        else:

            SLOT1_RED.off()


        # ==================================================
        # SLOT 2
        # ==================================================

        if slot2_state == "TOO CLOSE":

            if blink_state:

                SLOT2_RED.on()

            else:

                SLOT2_RED.off()

        elif slot2_state == "PARKED":

            SLOT2_RED.on()

        else:

            SLOT2_RED.off()


# ==========================================================
# DISPLAY SLOT 1
# ==========================================================

def display_slot1():

    print("SLOT 1")

    print("-" * 62)

    print(
        f"Distance          : "
        f"{slot1_distance:6.2f} cm"
    )

    print(
        f"Status            : "
        f"{slot1_state}"
    )


    if slot1_car_present:

        minutes = get_parking_minutes(
            slot1_start_time
        )

        charge = get_current_charge(
            slot1_start_time
        )

        print(
            f"Parking time      : "
            f"{minutes:6.2f} minutes"
        )

        print(
            f"Current charge    : "
            f"GH₵{charge:6.2f}"
        )

    else:

        print(
            "Parking time      : --"
        )

        print(
            "Current charge    : GH₵0.00"
        )


# ==========================================================
# DISPLAY SLOT 2
# ==========================================================

def display_slot2():

    print("SLOT 2")

    print("-" * 62)

    print(
        f"Distance          : "
        f"{slot2_distance:6.2f} cm"
    )

    print(
        f"Status            : "
        f"{slot2_state}"
    )


    if slot2_car_present:

        minutes = get_parking_minutes(
            slot2_start_time
        )

        charge = get_current_charge(
            slot2_start_time
        )

        print(
            f"Parking time      : "
            f"{minutes:6.2f} minutes"
        )

        print(
            f"Current charge    : "
            f"GH₵{charge:6.2f}"
        )

    else:

        print(
            "Parking time      : --"
        )

        print(
            "Current charge    : GH₵0.00"
        )


# ==========================================================
# DISPLAY DASHBOARD
# ==========================================================

def display_dashboard():

    clear_screen()


    print("=" * 62)

    print(
        "                 SMART PARKING SYSTEM"
    )

    print("=" * 62)

    print()


    # ======================================================
    # PARKING AVAILABILITY
    # ======================================================

    free_slots = available_slot_count()


    if free_slots > 0:

        parking_status = "AVAILABLE"

    else:

        parking_status = "FULL"


    print("PARKING AVAILABILITY")

    print("-" * 62)

    print(
        f"Status            : "
        f"{parking_status}"
    )

    print(
        f"Free slots        : "
        f"{free_slots} / 2"
    )

    print()


    # ======================================================
    # MAIN GATE
    # ======================================================

    print("MAIN ENTRANCE / EXIT GATE")

    print("-" * 62)


    if gate_is_open:

        gate_status = "OPEN"

    else:

        gate_status = "CLOSED"


    print(
        f"Gate status       : "
        f"{gate_status}"
    )

    print(
        f"Distance          : "
        f"{gate_distance:6.2f} cm"
    )


    # ======================================================
    # GATE TIMER
    # ======================================================

    if gate_is_open:

        if gate_open_time is not None:

            elapsed = (
                time() -
                gate_open_time
            )

            remaining = max(
                0,
                GATE_CLOSE_DELAY -
                elapsed
            )

            print(
                f"Gate closes in    : "
                f"{remaining:5.0f} seconds"
            )

    else:

        print(
            "Gate closes in    : --"
        )


    # ======================================================
    # GATE MESSAGE
    # ======================================================

    if gate_distance <= GATE_DETECT_DISTANCE:

        print(
            "Gate message      : "
            "CAR DETECTED"
        )

    elif gate_is_open:

        print(
            "Gate message      : "
            "GATE OPEN"
        )

    else:

        print(
            "Gate message      : "
            "WAITING FOR CAR"
        )


    print()


    # ======================================================
    # SLOT 1
    # ======================================================

    display_slot1()

    print()


    # ======================================================
    # SLOT 2
    # ======================================================

    display_slot2()

    print()


    # ======================================================
    # SYSTEM SETTINGS
    # ======================================================

    print("-" * 62)

    print(
        f"Parking rate      : "
        f"GH₵{RATE_PER_MINUTE:.2f} / minute"
    )

    print(
        f"Gate open time    : "
        f"{GATE_CLOSE_DELAY} seconds"
    )

    print(
        f"Gate detection    : "
        f"{GATE_DETECT_DISTANCE} cm"
    )

    print()


    # ======================================================
    # INDICATOR LEGEND
    # ======================================================

    print("INDICATORS")

    print("-" * 62)

    print(
        "GREEN      = Car detected"
    )

    print(
        "RED        = Parked"
    )

    print(
        "RED BLINK  = Car too close"
    )

    print(
        "BUZZER     = Too-close warning"
    )

    print()


    print("=" * 62)

    print(
        "Press Ctrl+C to stop"
    )

    print("=" * 62)


# ==========================================================
# SYSTEM START
# ==========================================================

clear_screen()


print("=" * 62)

print(
    "                 SMART PARKING SYSTEM"
)

print("=" * 62)

print()

print("Initializing system...")

print()


# ==========================================================
# HARDWARE INFORMATION
# ==========================================================

print("MAIN GATE")

print("Trigger : GPIO 6")

print("Echo    : GPIO 13")

print("Servo   : GPIO 5")

print()


print("SLOT 1")

print("Trigger : GPIO 18")

print("Echo    : GPIO 17")

print("Red     : GPIO 27")

print("Green   : GPIO 22")

print("Buzzer  : GPIO 26")

print()


print("SLOT 2")

print("Trigger : GPIO 21")

print("Echo    : GPIO 20")

print("Red     : GPIO 23")

print("Green   : GPIO 24")

print("Buzzer  : GPIO 19")

print()


print(
    f"Parking rate: "
    f"GH₵{RATE_PER_MINUTE:.2f} / minute"
)

print(
    f"Gate open time: "
    f"{GATE_CLOSE_DELAY} seconds"
)

print()

print("SYSTEM READY")

print()


# ==========================================================
# MAIN LOOP
# ==========================================================

try:

    while True:

        # ----------------------------------------------
        # UPDATE SLOT 1
        # ----------------------------------------------

        update_slot1()


        # ----------------------------------------------
        # UPDATE SLOT 2
        # ----------------------------------------------

        update_slot2()


        # ----------------------------------------------
        # UPDATE MAIN GATE
        # ----------------------------------------------

        update_gate()


        # ----------------------------------------------
        # UPDATE WARNING LIGHTS
        # ----------------------------------------------

        update_warning_lights()


        # ----------------------------------------------
        # DISPLAY DASHBOARD
        # ----------------------------------------------

        display_dashboard()


        # ----------------------------------------------
        # LOOP SPEED
        # ----------------------------------------------

        sleep(0.25)


# ==========================================================
# STOP SYSTEM
# ==========================================================

except KeyboardInterrupt:

    print()

    print(
        "Stopping Smart Parking System..."
    )


# ==========================================================
# CLEANUP
# ==========================================================

finally:

    # ------------------------------------------------------
    # SLOT 1
    # ------------------------------------------------------

    SLOT1_RED.off()

    SLOT1_GREEN.off()

    SLOT1_BUZZER.off()


    # ------------------------------------------------------
    # SLOT 2
    # ------------------------------------------------------

    SLOT2_RED.off()

    SLOT2_GREEN.off()

    SLOT2_BUZZER.off()


    # ------------------------------------------------------
    # SERVO
    # ------------------------------------------------------
    #
    # No servo command is sent here.
    #
    # The SG90 remains in its current position.
    #

    print()

    print("All LEDs OFF.")

    print("All buzzers OFF.")

    print("Servo position unchanged.")

    print("System safely stopped.")

