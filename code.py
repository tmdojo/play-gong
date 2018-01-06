# play-gong
# Tap to play a gong sound with fancy lightings
# Author: Shunya Sato

import time, random

import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import audioio
import neopixel

import adafruit_lis3dh

# enable the speaker
spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = Direction.OUTPUT
spkrenable.value = True

# Hardware I2C setup on CircuitPlayground Express:
i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# Set tap detection to double taps.  The first parameter is a value:
#  - 0 = Disable tap detection.
#  - 1 = Detect single taps.
#  - 2 = Detect double taps.
# The second parameter is the threshold and a higher value means less sensitive
# tap detection.  Note the threshold should be set based on the range above:
#  - 2G = 40-80 threshold
#  - 4G = 20-40 threshold
#  - 8G = 10-20 threshold
#  - 16G = 5-10 threshold
lis3dh.set_tap(1, 80)

# make the 2 input buttons
buttonA = DigitalInOut(board.BUTTON_A)
buttonA.direction = Direction.INPUT
buttonA.pull = Pull.DOWN

n_pixels = 10
pixels = neopixel.NeoPixel(board.NEOPIXEL, n_pixels, auto_write=False)

# "gong.wav" is for external speaker
# Use "gong-4db.wav" for internal speaker with lower volume
# "gong-54db.wav" is for debugging silently at night...
audiofiles = ["gong-4db.wav", "gong-54db.wav", "gong.wav"]

filename = audiofiles[0]
f = open(filename, "rb")
audio = audioio.AudioOut(board.A0, f)
ticker = 0
pattern = 0

# Idea is taken from https://github.com/adafruit/Adafruit_Python_WS2801/blob/master/examples/rainbow.py
# Define the wheel function to interpolate between different hues.
def wheel(pos):
    """ Takes pos value (0-255) and return RGB color in wheel """
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def reset_pixels():
    """ set all neopixel to off """
    for i in range(n_pixels):
        pixels[i] = (0,0,0)

def set_pixels(mycolor):
    """ set all neopixel to mycolor """
    for i in range(n_pixels):
        pixels[i] = mycolor

def set_ranbow():
    """ set pixel color in rainbow according to its position """
    for i in range(n_pixels):
        pixels[i] = wheel(int(i * (256/n_pixels)))

def lights_off():
    """ turn off all neopixels """
    reset_pixels()
    pixels.show()

def lights_flash(framei, colori = 0):
    """ flash neopixel on/off """
    if framei%2:
        # turn off in every other frame
        reset_pixels()
    else:
        if colori == 0: # white
            selected_color = (255, 255, 255)
            set_pixels(selected_color)
        elif colori == 1: # rainbow according to position
            set_ranbow()
        elif colori == 2: # random rainbow
            selected_color = wheel(random.randrange(256))
            set_pixels(selected_color)
    pixels.show()

def lights_rotate(framei, colori = 0):
    """ turn on neopixel one by one in rotation """
    reset_pixels()
    if colori == 0: # white
        pixels[framei%10] = (255,255,255)
    elif colori == 1: # rainbow according to position
        pixels[framei%10] = wheel(int((framei%10) * (256 / 10)))
    elif colori == 2: # random rainbow
        pixels[framei%10] = wheel(random.randrange(256))
    pixels.show()

def play_lights(pattern, framei):
    """ play selected lighting effect """
    if pattern == 0:
        lights_flash(framei, 0)
    elif pattern == 1:
        lights_flash(framei, 1)
    elif pattern == 2:
        lights_flash(framei, 2)
    elif pattern == 3:
        lights_rotate(framei, 0)
    elif pattern == 4:
        lights_rotate(framei, 1)
    elif pattern == 5:
        lights_rotate(framei, 2)

def play_file():
    """ play audio file """
    if audio.playing:
        audio.stop()
    audio.play()

while True:
    tap = lis3dh.tapped | buttonA.value # you can activate by tapping or pressing buttonA
    if tap:
        print("tap!")
        ticker = 0
        pattern = random.randrange(6) # select lighting pattern
        play_file()
        time.sleep(0.1) # crude debounce
    if audio.playing:
        print("playing audio: {}-{}".format(pattern, ticker))
        play_lights(pattern, ticker)
        #lights_rotate(ticker, colori = 2)
        #lights_flash(ticker, colori = 2)
        ticker += 1
        time.sleep(0.05) # this sets frame rate for lighting animation
    elif ticker > 0:
        print("Turn off lights")
        ticker = 0
        lights_off()
