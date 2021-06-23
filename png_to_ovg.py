from PIL import Image
from numpy import binary_repr
from io import StringIO

# Work in progress! Doesn't work yet at all.

# Credits/sources in ovg_to_png.py

filename = "ovg.png"
outfile = "output.ovg"

finalBytes = b""


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


def output_bitstream(pixels, compressed, cmdBlock):
    # print(f"Bitstream {compressed}: {cmdBlock} // {pixels}")
    # print(bitstring_to_bytes(f"{cmdBlock}{pixels}"))
    global finalBytes
    finalBytes = finalBytes + bitstring_to_bytes(f"{cmdBlock}{pixels}")


# todo: pixels to be a list we can iterate through
def construct_bitstream(count, pixels, compressed):
    # print(f"Pixel input: {count}, {pixels}, {compressed}")
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
        count = count - binary_max - 1
    # If any are left after that, output them too
    # fixme: just do this in the loop above?
    if count > 0:
        cmdBlock = str(compressed) + binary_repr(count - 1, 7)
        if compressed:
            bitsOut = pixels
        else:
            bitsOut = sio.read(count * 32)  # 32bpp RRGGBBAA
            # print(f"Bitsout: {bitsOut}, Count: {count * 32}")
        output_bitstream(bitsOut, compressed, cmdBlock)


def pixels_to_binary(pixel):
    # 0 opacity black -> 0 opacity white
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    a = pixel[3]
    if r == 0 and g == 0 and b == 0 and a == 0:
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
for pixelIndex in range(len(pixels)):
    pixel = pixels[pixelIndex]
    # print(pixel)
    if pixel == lastPixel:
        # A repeat.
        repeatCount = repeatCount + 1
        if uniqueCount > 0:
            # print(f"ended a run of uniques. there were {uniqueCount} unique pixels: {uniqueOutput}")
            construct_bitstream(uniqueCount, uniqueOutput, 0)
            uniqueCount = 0
    else:
        # A new pixel.
        if pixelIndex > 0:
            uniqueCount = uniqueCount + 1
            nextUnique = pixels[pixelIndex - 1]
            # print(f"unique added: {pixelIndex} {nextUnique}")
            uniqueOutput = f"{uniqueOutput}{pixels_to_binary(nextUnique)}"
        # Now, what to do with that information. Were we previously on a roll?
        if repeatCount > 0:
            repeatCount = repeatCount + 1
            # print(f"ended a run of repeats. there were {repeatCount} repeated pixels of {lastPixel} - {pixels_to_binary(lastPixel)}.")
            construct_bitstream(repeatCount, pixels_to_binary(lastPixel), 1)
            # end run
            repeatCount = 0
            # was not unique
            uniqueCount = 0
            uniqueOutput = ""
    lastPixel = pixel

# loop ended. check accumulators
# fixme: dry
if repeatCount > 0:
    repeatCount = repeatCount + 1
    # print(f"ended a run of repeats. there were {repeatCount} repeated pixels of {lastPixel} - {pixels_to_binary(lastPixel)}.")
    construct_bitstream(repeatCount, pixels_to_binary(lastPixel), 1)
    # end run
    repeatCount = 0
    # was not unique
    uniqueCount = 0
    uniqueOutput = ""
if uniqueCount > 0:
    # print(f"ended a run of uniques. there were {uniqueCount} unique pixels: {uniqueOutput}")
    construct_bitstream(uniqueCount, uniqueOutput, 0)
    uniqueCount = 0

f = open(outfile, "wb")
print(f"saved as {outfile}")
f.write(finalBytes)
f.close()