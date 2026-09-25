
from gpiozero import DistanceSensor, LED, Buzzer, AngularServo
from time import sleep, time
import os


# ==========================================================
#                  SMART PARKING SYSTEM
# ==========================================================


# ==========================================================
# PARKING RATE
# ==========================================================

RATE_PER_MINUTE = 1.00       # GH₵1.00 per minute


# ==========================================================
# PARKING SLOT DISTANCES
# ==========================================================

TOO_CLOSE_DISTANCE = 4
CLOSE_DISTANCE = 15
FAR_DISTANCE = 25


# ==========================================================
# MAIN GATE DETECTION
# ==========================================================

GATE_DETECT_DISTANCE = 20


# ==========================================================
# MAIN GATE OPEN TIME
# ==========================================================

GATE_CLOSE_DELAY = 10


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
# MG90S SERVO
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
# NEW:
# INCOMING CAR SLOT ASSIGNMENT
# ==========================================================
#
# These variables are different from car_present.
#
# RESERVED means:
# "This slot has been assigned to an incoming car,
#  but the car has not reached the parking sensor yet."
#
# This prevents another incoming car from receiving
# the same parking slot.
#


slot1_reserved = False
slot2_reserved = False


# ==========================================================
# WHICH SLOT WAS ASSIGNED TO THE INCOMING CAR?
# ==========================================================

assigned_slot = None


# ==========================================================
# PREVENT REPEATED ASSIGNMENT
# ==========================================================
#
# When a car remains in front of the main gate sensor,
# the loop runs many times per second.
#
# We therefore need to know whether this car has
# already been assigned a parking slot.
#

incoming_car_assigned = False


# ==========================================================
# MAIN GATE VARIABLES
# ==========================================================

gate_distance = 0

gate_is_open = False

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
# FIND A FREE PARKING SLOT
# ==========================================================

def find_free_slot():

    # ------------------------------------------------------
    # SLOT 1
    # ------------------------------------------------------

    if (
        not slot1_car_present
        and
        not slot1_reserved
    ):

        return 1


    # ------------------------------------------------------
    # SLOT 2
    # ------------------------------------------------------

    if (
        not slot2_car_present
        and
        not slot2_reserved
    ):

        return 2


    # ------------------------------------------------------
    # NO SLOT
    # ------------------------------------------------------

    return None


# ==========================================================
# ASSIGN PARKING SLOT TO INCOMING CAR
# ==========================================================

def assign_parking_slot():

    global slot1_reserved
    global slot2_reserved
    global assigned_slot
    global incoming_car_assigned


    # ------------------------------------------------------
    # Do not assign twice to the same incoming vehicle
    # ------------------------------------------------------

    if incoming_car_assigned:

        return assigned_slot


    # ------------------------------------------------------
    # Find free slot
    # ------------------------------------------------------

    free_slot = find_free_slot()


    # ------------------------------------------------------
    # NO FREE SLOT
    # ------------------------------------------------------

    if free_slot is None:

        print()
        print("==============================================")
        print("           PARKING FULL")
        print("==============================================")
        print("Incoming vehicle was NOT assigned a slot.")
        print()

        return None


    # ======================================================
    # ASSIGN SLOT 1
    # ======================================================

    if free_slot == 1:

        slot1_reserved = True

        assigned_slot = 1


    # ======================================================
    # ASSIGN SLOT 2
    # ======================================================

    elif free_slot == 2:

        slot2_reserved = True

        assigned_slot = 2


    # ======================================================
    # SAVE ASSIGNMENT
    # ======================================================

    incoming_car_assigned = True


    print()
    print("==============================================")
    print("        INCOMING VEHICLE ASSIGNED")
    print("==============================================")

    print(
        f"Assigned parking slot : SLOT {assigned_slot}"
    )

    print("Gate                  : OPEN")

    print("==============================================")
    print()


    return assigned_slot


# ==========================================================
# CLEAR INCOMING ASSIGNMENT
# ==========================================================
#
# This is called when the incoming vehicle reaches
# its assigned slot.
#
# The reservation changes into actual occupancy.
#


def confirm_slot_arrival(slot_number):

    global slot1_reserved
    global slot2_reserved
    global assigned_slot
    global incoming_car_assigned


    if slot_number == 1:

        slot1_reserved = False


    elif slot_number == 2:

        slot2_reserved = False


    # Assignment has now become actual parking
    assigned_slot = None

    incoming_car_assigned = False


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

        # Start gate timer immediately
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
# NUMBER OF AVAILABLE SLOTS
# ==========================================================
#
# IMPORTANT:
#
# A reserved slot is NOT considered free.
#
# This prevents an incoming car from being assigned
# the same slot as another incoming car.
#


def available_slot_count():

    count = 0


    if (
        not slot1_car_present
        and
        not slot1_reserved
    ):

        count += 1


    if (
        not slot2_car_present
        and
        not slot2_reserved
    ):

        count += 1


    return count


# ==========================================================
# PARKING TIME
# ==========================================================

def get_parking_minutes(start_time):

    if start_time is None:

        return 0


    elapsed_seconds = (
        time() -
        start_time
    )


    return elapsed_seconds / 60


# ==========================================================
# CURRENT PARKING CHARGE
# ==========================================================

def get_current_charge(start_time):

    minutes = get_parking_minutes(
        start_time
    )


    return (
        minutes *
        RATE_PER_MINUTE
    )


# ==========================================================
# UPDATE SLOT 1
# ==========================================================

def update_slot1():

    global slot1_distance
    global slot1_state
    global slot1_car_present
    global slot1_start_time
    global slot1_was_occupied


    # ------------------------------------------------------
    # READ SENSOR
    # ------------------------------------------------------

    distance = (
        SLOT1_SENSOR.distance *
        100
    )


    slot1_distance = distance


    # ======================================================
    # TOO CLOSE
    # ======================================================

    if distance < TOO_CLOSE_DISTANCE:

        slot1_state = "TOO CLOSE"

        SLOT1_GREEN.off()

        SLOT1_BUZZER.on()


    # ======================================================
    # PARKED
    # ======================================================

    elif distance < CLOSE_DISTANCE:

        slot1_state = "PARKED"

        SLOT1_RED.on()

        SLOT1_GREEN.off()

        SLOT1_BUZZER.off()


    # ======================================================
    # CAR DETECTED
    # ======================================================

    elif distance <= FAR_DISTANCE:

        slot1_state = "CAR DETECTED"

        SLOT1_RED.off()

        SLOT1_GREEN.on()

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
    # VEHICLE ENTERED SLOT 1
    # ======================================================

    if distance <= FAR_DISTANCE:

        if not slot1_car_present:

            slot1_start_time = time()

            slot1_car_present = True

            slot1_was_occupied = True


            # ----------------------------------------------
            # IF THIS WAS THE ASSIGNED INCOMING CAR
            # ----------------------------------------------

            if (
                assigned_slot == 1
            ):

                confirm_slot_arrival(1)


    # ======================================================
    # VEHICLE LEFT SLOT 1
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
                elapsed_seconds /
                60
            )


            # ----------------------------------------------
            # CALCULATE PAYMENT
            # ----------------------------------------------

            amount = (
                elapsed_minutes *
                RATE_PER_MINUTE
            )


            # ----------------------------------------------
            # PAYMENT
            # ----------------------------------------------

            print()

            print("=" * 55)

            print(
                "                  SLOT 1 PAYMENT"
            )

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
            # OUTGOING CAR
            # ----------------------------------------------
            #
            # IMPORTANT:
            #
            # This opens the gate for EXIT.
            #
            # It DOES NOT assign another parking slot.
            #

            if slot1_was_occupied:

                print(
                    ">>> SLOT 1 EXIT VEHICLE"
                )

                print(
                    ">>> NO PARKING SLOT ASSIGNED"
                )

                print(
                    ">>> OPENING MAIN GATE"
                )


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


    # ------------------------------------------------------
    # READ SENSOR
    # ------------------------------------------------------

    distance = (
        SLOT2_SENSOR.distance *
        100
    )


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
    # VEHICLE ENTERED SLOT 2
    # ======================================================

    if distance <= FAR_DISTANCE:

        if not slot2_car_present:

            slot2_start_time = time()

            slot2_car_present = True

            slot2_was_occupied = True


            # ----------------------------------------------
            # IF THIS WAS THE ASSIGNED INCOMING CAR
            # ----------------------------------------------

            if (
                assigned_slot == 2
            ):

                confirm_slot_arrival(2)


    # ======================================================
    # VEHICLE LEFT SLOT 2
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
                elapsed_seconds /
                60
            )


            # ----------------------------------------------
            # CALCULATE PAYMENT
            # ----------------------------------------------

            amount = (
                elapsed_minutes *
                RATE_PER_MINUTE
            )


            # ----------------------------------------------
            # PAYMENT
            # ----------------------------------------------

            print()

            print("=" * 55)

            print(
                "                  SLOT 2 PAYMENT"
            )

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
            # OUTGOING CAR
            # ----------------------------------------------
            #
            # IMPORTANT:
            #
            # No new slot is assigned.
            #

            if slot2_was_occupied:

                print(
                    ">>> SLOT 2 EXIT VEHICLE"
                )

                print(
                    ">>> NO PARKING SLOT ASSIGNED"
                )

                print(
                    ">>> OPENING MAIN GATE"
                )


                open_gate()


                slot2_was_occupied = False


# ==========================================================
# UPDATE MAIN GATE
# ==========================================================

def update_gate():

    global gate_distance
    global gate_open_time
    global incoming_car_assigned


    # ------------------------------------------------------
    # READ SENSOR
    # ------------------------------------------------------

    distance = (
        GATE_SENSOR.distance *
        100
    )


    gate_distance = distance


    # ======================================================
    # CAR DETECTED AT MAIN GATE
    # ======================================================

    if distance <= GATE_DETECT_DISTANCE:


        # --------------------------------------------------
        # INCOMING VEHICLE
        # --------------------------------------------------
        #
        # Only assign a parking slot if this vehicle
        # has not already been assigned one.
        #

        if not incoming_car_assigned:


            # ----------------------------------------------
            # ASSIGN A FREE SLOT
            # ----------------------------------------------

            assigned = (
                assign_parking_slot()
            )


            # ----------------------------------------------
            # OPEN GATE
            # ----------------------------------------------
            #
            # The gate opens after detecting the car.
            #

            if assigned is not None:

                open_gate()


    # ======================================================
    # GATE TIMER
    # ======================================================

    if gate_is_open:


        if gate_open_time is None:

            gate_open_time = time()


        elapsed = (
            time() -
            gate_open_time
        )


        # --------------------------------------------------
        # CLOSE GATE AFTER DELAY
        # --------------------------------------------------

        if elapsed >= GATE_CLOSE_DELAY:

            close_gate()


# ==========================================================
# RESET INCOMING VEHICLE DETECTION
# ==========================================================
#
# Once the vehicle leaves the main-gate sensor,
# allow the next vehicle to be treated as a new
# incoming vehicle.
#
# IMPORTANT:
# This does NOT remove the parking-slot assignment.
#
# The assignment remains reserved until the car reaches
# the assigned parking slot.
#


def update_incoming_vehicle_state():

    global incoming_car_assigned


    if (
        gate_distance >
        GATE_DETECT_DISTANCE
    ):

        # The incoming vehicle has cleared
        # the main gate sensor.
        #
        # If its parking slot has not yet been reached,
        # keep the reservation.
        #
        # Only reset the detection flag so another car
        # can be detected later.

        if (
            slot1_car_present
            or
            slot2_car_present
        ):

            # Nothing required here.
            pass


# ==========================================================
# UPDATE BLINKING WARNING LIGHTS
# ==========================================================

def update_warning_lights():

    global last_blink_time
    global blink_state


    current_time = time()


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


    # ------------------------------------------------------
    # RESERVED
    # ------------------------------------------------------

    if slot1_reserved:

        print(
            "Assignment        : "
            "RESERVED"
        )


    elif slot1_car_present:

        print(
            "Assignment        : "
            "OCCUPIED"
        )


    else:

        print(
            "Assignment        : "
            "FREE"
        )


    # ------------------------------------------------------
    # PARKING TIME
    # ------------------------------------------------------

    if slot1_car_present:

        minutes = (
            get_parking_minutes(
                slot1_start_time
            )
        )


        charge = (
            get_current_charge(
                slot1_start_time
            )
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
            "Current charge    : "
            "GH₵0.00"
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


    # ------------------------------------------------------
    # RESERVED
    # ------------------------------------------------------

    if slot2_reserved:

        print(
            "Assignment        : "
            "RESERVED"
        )


    elif slot2_car_present:

        print(
            "Assignment        : "
            "OCCUPIED"
        )


    else:

        print(
            "Assignment        : "
            "FREE"
        )


    # ------------------------------------------------------
    # PARKING TIME
    # ------------------------------------------------------

    if slot2_car_present:

        minutes = (
            get_parking_minutes(
                slot2_start_time
            )
        )


        charge = (
            get_current_charge(
                slot2_start_time
            )
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
            "Current charge    : "
            "GH₵0.00"
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

    free_slots = (
        available_slot_count()
    )


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
    # CURRENT INCOMING ASSIGNMENT
    # ======================================================

    print("INCOMING VEHICLE")

    print("-" * 62)


    if assigned_slot is not None:

        print(
            f"Assigned slot     : "
            f"SLOT {assigned_slot}"
        )

    else:

        print(
            "Assigned slot     : NONE"
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

    if (
        gate_distance <=
        GATE_DETECT_DISTANCE
    ):

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
        # UPDATE DASHBOARD
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

    # No servo command here.
    # Servo remains at its current position.


    print()

    print("All LEDs OFF.")

    print("All buzzers OFF.")

    print("Servo position unchanged.")

    print("System safely stopped.")

