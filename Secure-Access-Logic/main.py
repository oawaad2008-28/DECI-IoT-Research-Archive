import machine
import time
import re
from utime import sleep

BUTTON_COUNT = 3
LED_COUNT = 8
INPUT_COUNT = 4

BUTTON_START_ID = 16
LED_GPIO_START = 8
last_button_time_stamp = 0
key_presses = []

# Extract the numeric pin id from the passed-in Pin instance
def PinId(pin):
    match = re.search(r'GPIO(\d+)', str(pin))
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Unable to extract pin ID from: {pin}")

def interrupt_callback(pin):
    global last_button_time_stamp
    
    cur_button_ts = time.ticks_ms()
    button_press_delta = cur_button_ts - last_button_time_stamp
    if button_press_delta > 200:
        last_button_time_stamp = cur_button_ts
        key_presses.append(PinId(pin))  # Store the numeric pin ID
        print(f'key press: {PinId(pin) - BUTTON_START_ID}')

def main():
    global key_presses
    global last_button_time_stamp
    PASSCODE_LENGTH = 0

    s0 = machine.Pin(27, machine.Pin.OUT)
    s1 = machine.Pin(28, machine.Pin.OUT)

    mux_in = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)

    buttons = []
    for btn_idx in range(BUTTON_COUNT):
        pin = machine.Pin(BUTTON_START_ID + btn_idx, machine.Pin.IN, machine.Pin.PULL_DOWN)
        buttons.append(pin)
        pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrupt_callback)

    PASS_CODE = [PinId(buttons[0]), PinId(buttons[2]), PinId(buttons[1])]
    PASSCODE_LENGTH = len(PASS_CODE)

    out_pins = []
    for out_id in range(LED_COUNT):
        out_pins.append(machine.Pin(LED_GPIO_START + out_id, machine.Pin.OUT))

    last_dev = -1
    while True:
        binary_code = 0
        for selector_val in range(INPUT_COUNT):
            s0.value(selector_val % 2)
            s1.value(selector_val // 2)
            sleep(0.02)
            binary_code += (pow(2, selector_val) * mux_in.value())

        if last_dev != binary_code:
            last_dev = binary_code
            print(f'selected output: {last_dev}')
        sleep(0.1)

        if len(key_presses) >= PASSCODE_LENGTH:
            if key_presses[:PASSCODE_LENGTH] == PASS_CODE:
                print('correct passcode')
                if binary_code < LED_COUNT:
                    print(f'toggling: {binary_code}')
                    out_pins[binary_code].toggle()
                else:
                    print(f'invalid output: {binary_code}, valid range: 0-{len(out_pins) - 1}, doing nothing')
            else:
                print('wrong passcode')
            print('')
            key_presses = key_presses[PASSCODE_LENGTH:]

if __name__ == "__main__":
    main()
