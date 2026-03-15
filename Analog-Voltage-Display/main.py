# imports
import machine
import time

#######################################
# Pin and constant definitions
#######################################

# Segment pins: A to DP on GP0 to GP7
segment_pins = [machine.Pin(i, machine.Pin.OUT) for i in range(0, 8)]

# Digit control pins: DIG1-GP11, DIG2-GP10, DIG3-GP9, DIG4-GP8
digit_pins = [
    machine.Pin(11, machine.Pin.OUT),  # DIG1
    machine.Pin(10, machine.Pin.OUT),  # DIG2
    machine.Pin(9, machine.Pin.OUT),   # DIG3
    machine.Pin(8, machine.Pin.OUT)    # DIG4
]

# ADC and Button
adc_pin = machine.ADC(26)  # Analog sensors
button_pin = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)

#######################################
# Global variables
#######################################
display_value = 0
display_timer = None
current_digit_index = 0

# Segment encoding for digits 0-9
digit_encoding = {
    0: [1,1,1,1,1,1,0,0],
    1: [0,1,1,0,0,0,0,0],
    2: [1,1,0,1,1,0,1,0],
    3: [1,1,1,1,0,0,1,0],
    4: [0,1,1,0,0,1,1,0],
    5: [1,0,1,1,0,1,1,0],
    6: [1,0,1,1,1,1,1,0],
    7: [1,1,1,0,0,0,0,0],
    8: [1,1,1,1,1,1,1,0],
    9: [1,1,1,1,0,1,1,0]
}

#######################################
# Function definitions
#######################################

def read_analogue_voltage():
    global display_value
    raw = adc_pin.read_u16()
    voltage = (raw / 65535.0) * 3.3
    display_value = int(voltage * 1000)
    print(f"[BUTTON PRESSED] Raw: {raw} -> Voltage: {voltage:.2f}V -> Display: {display_value}")

def scan_display(timer):
    global current_digit_index, display_value

    # Turn off all digits
    for dp in digit_pins:
        dp.value(1)

    val_str = f"{display_value:04d}"
    digit_val = int(val_str[current_digit_index])
    display_digit(digit_val, current_digit_index)

    current_digit_index = (current_digit_index + 1) % 4

def display_digit(digit_value, digit_index, dp_enable=False):
    segments = digit_encoding.get(digit_value, [0]*8)
    if dp_enable:
        segments[7] = 1  # Turn on decimal point
    for pin, val in zip(segment_pins, segments):
        pin.value(val)
    digit_pins[digit_index].value(0)  # Activate the digit (active LOW)

def setup():
    global display_value
    print("[SYSTEM] Setup started...")
    display_value = 0  # Initialize display to 0000
    update_display()   # Ensure display shows 0000 on start
    enable_display_timer()
    print("[SYSTEM] Display timer enabled.")

def enable_display_timer():
    global display_timer
    display_timer = machine.Timer()
    display_timer.init(freq=800, mode=machine.Timer.PERIODIC, callback=scan_display)

def update_display():
    # This function will update the display to show the current value
    val_str = f"{display_value:04d}"
    for i, digit in enumerate(val_str):
        display_digit(int(digit), i)

#######################################
# Main
#######################################
if __name__ == '__main__':
    setup()
    last_state = 0
    while True:
        current_state = button_pin.value()
        if current_state and not last_state:
            read_analogue_voltage()
        last_state = current_state
        time.sleep_ms(50)
