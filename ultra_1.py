
from gpiozero import DistanceSensor, LED
from time import sleep

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


# ==================================================
# DISTANCE SETTINGS
# ==================================================

CLOSE_DISTANCE = 20       # Less than 20 cm = RED
FAR_DISTANCE = 100        # 20-100 cm = GREEN
                           # More than 100 cm = BOTH OFF


# ==================================================
# SLOT 1 ONLY
# ==================================================

def update_slot1():

    distance = SLOT1_SENSOR.distance * 100

    if distance < CLOSE_DISTANCE:

        SLOT1_RED.on()
        SLOT1_GREEN.off()

        status = "CLOSE"

    elif distance <= FAR_DISTANCE:

        SLOT1_RED.off()
        SLOT1_GREEN.on()

        status = "FAR"

    else:

        SLOT1_RED.off()
        SLOT1_GREEN.off()

        status = "EMPTY"

    print(f"Slot 1: {distance:.2f} cm - {status}")


# ==================================================
# SLOT 2 ONLY
# ==================================================

def update_slot2():

    distance = SLOT2_SENSOR.distance * 100

    if distance < CLOSE_DISTANCE:

        SLOT2_RED.on()
        SLOT2_GREEN.off()

        status = "CLOSE"

    elif distance <= FAR_DISTANCE:

        SLOT2_RED.off()
        SLOT2_GREEN.on()

        status = "FAR"

    else:

        SLOT2_RED.off()
        SLOT2_GREEN.off()

        status = "EMPTY"

    print(f"Slot 2: {distance:.2f} cm - {status}")


# ==================================================
# MAIN PROGRAM
# ==================================================

print("Two-Slot Parking Sensor")
print("Each sensor controls only its own slot.")
print("Press Ctrl+C to stop.")
print()

try:

    while True:

        # Sensor 1 controls ONLY Slot 1
        update_slot1()

        # Sensor 2 controls ONLY Slot 2
        update_slot2()

        print("----------------------------")

        sleep(0.5)


except KeyboardInterrupt:

    print("\nSystem stopped.")


finally:

    # Turn everything OFF
    SLOT1_RED.off()
    SLOT1_GREEN.off()

    SLOT2_RED.off()
    SLOT2_GREEN.off()

