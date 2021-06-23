from PIL import Image
from numpy import binary_repr

# Work in progress!

# Credits/sources in ovg_to_png.py

filename = "ovg.png"

img = Image.open(filename)
pixels = list(img.getdata())

print(f"Total pixels: {len(pixels)}")

lastPixel = None
repeatCount = 0
uniqueCount = 0
uniqueOutput = ""

bytesOut = bytearray()


def construct_bitstream(count, pixels, compressed):
    if compressed:
        # rle compressed repetition
        while count > 127:
            # Make sure we don't overflow
            count = count - 127
            cmdBlock = "11111111"
            print(f"Bitstream: Command block {cmdBlock} then 127 pixels, all {pixels}")
        if count > 0:
            # Print any remainder now that the 127 blocks are dealt with
            cmdBlock = "1" + binary_repr(count, 7)
            print(f"Bitstream: Command block {cmdBlock} then {count} pixels, all {pixels}")
        return True
    else:
        # uniques, possibly more than one!
        cmdBlock = "0" + binary_repr(count, 7)
        print(f"Bitstream: Command block {cmdBlock} then {count} unique pixels follow: {pixels}")
        return True


# Loop over every pixel in the loaded image
for pixel in pixels:
    # Pixel was the same. Add to the tally and continue.
    if pixel == lastPixel:
        repeatCount = repeatCount + 1
        continue
    # A new pixel colour!
    if repeatCount == 0:
        # First pixel of the image; record it
        lastPixel = pixel
        continue
    if repeatCount > 1:
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
        print(f"> {repeatCount}\t repeat pixels ready - needs pixel count and RLE repeat flag")
        # Construct output
        construct_bitstream(repeatCount, pixel, 1)
        repeatCount = 0
        continue
    # This is a unique pixel; start a run of uniques
    uniqueCount = uniqueCount + 1
    uniqueOutput = f"{uniqueOutput} {pixel}"
    repeatCount = 0

# to do: construct bitstream; the above human-readable output appears correct