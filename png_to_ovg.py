import numpy as np
from PIL import Image
from numpy import binary_repr
from io import StringIO

# Work in progress! Doesn't work yet at all.

# Credits/sources in ovg_to_png.py

filename = "ovg.png"

finalBytes = b""


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


def output_bitstream(pixels, compressed, cmdBlock):
    print(f"Bitstream {compressed}: {cmdBlock} // {pixels}")
    print(bitstring_to_bytes(f"{cmdBlock}{pixels}"))
    global finalBytes
    finalBytes = finalBytes + bitstring_to_bytes(f"{cmdBlock}{pixels}")


# todo: pixels to be a list we can iterate through
def construct_bitstream(count, pixels, compressed):
    count = count - 1  # pdf spec fix
    print(f"Pixel input: {count}, {pixels}, {compressed}")
    # Make it a string we can read like a file
    sio = StringIO(pixels)
    # Figure out our overflow (127, spoilers)
    binary_max = int("1111111", 2)
    # Start churning through the string using binary_max chunks
    while count > binary_max:
        cmdBlock = str(compressed) + binary_repr(binary_max, 7)
        if compressed:
            bitsOut = pixels
        else:
            bitsOut = sio.read(binary_max * 4)  # 32bpp RRGGBBAA
        output_bitstream(bitsOut, compressed, cmdBlock)
        count = count - binary_max
    # If any are left after that, output them too
    # fixme: just do this in the loop above?
    if count > 0:
        cmdBlock = str(compressed) + binary_repr(count, 7)
        if compressed:
            bitsOut = pixels
        else:
            bitsOut = sio.read(count * 32)  # 32bpp RRGGBBAA
            print(f"Bitsout: {bitsOut}, Count: {count * 32}")
        output_bitstream(bitsOut, compressed, cmdBlock)


def pixels_to_binary(pixel):
    # 0 opacity black -> 0 opacity white
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    a = pixel[3]
    if r == 0 & g == 0 & b == 0 & a == 0:
        r = 255
        g = 255
        b = 255
    r = binary_repr(r, 8)
    g = binary_repr(g, 8)
    b = binary_repr(b, 8)
    a = binary_repr(a, 8)
    return f"{r}{g}{b}{a}"


# Parse image
img = Image.open(filename)
pixels = list(img.getdata())
print(f"Total pixels: {len(pixels)}")

# Counters
lastPixel = None
repeatCount = 0
uniqueCount = 0
uniqueOutput = ""

# Loop over every pixel in the loaded image
for pixel in pixels:
    # Pixel was the same. Add to the tally.
    if pixel == lastPixel:
        repeatCount = repeatCount + 1
        continue
    # A new pixel colour!
    if repeatCount == 0:
        # First pixel of the image; record it
        lastPixel = pixel
        continue
    if repeatCount > 2:
        if uniqueCount > 0:
            # We just ended a run of unique pixels.
            print(f"> {uniqueCount}\t unique pixels ready - needs pixel count but no RLE repeat flag")
            # Construct output
            construct_bitstream(uniqueCount, uniqueOutput, 0)
            # Reset unique accumulators
            uniqueOutput = ""
            uniqueCount = 0
            continue
        # We just ended a run of repeated pixels
        print(f"> {repeatCount}\t repeat pixels of {pixel} ready - needs pixel count and RLE repeat flag")
        # Construct output
        construct_bitstream(repeatCount, pixels_to_binary(pixel), 1)
        repeatCount = 0
        continue
    # This is a unique pixel; start a run of uniques
    uniqueCount = uniqueCount + 1
    # Concatenate and construct output
    uniqueOutput = f"{uniqueOutput}{pixels_to_binary(pixel)}"
    repeatCount = 0

f = open("output.ovg", "wb")
f.write(finalBytes)
f.close()