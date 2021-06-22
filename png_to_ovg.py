from PIL import Image
from numpy import binary_repr

# Work in progress!

# Credits/sources in ovg_to_png.py

filename = "ovg.png"

img = Image.open(filename)
pixels = list(img.getdata())

print(f"Total pixels: {len(pixels)}")

lastPixel = None
groupCount = 0
currentUniques = 0
uniqueOutput = ""

bytesOut = bytearray()

for pixel in pixels:
    if pixel == lastPixel:
        # Pixel was the same. Start a group.
        groupCount = groupCount + 1
    else:
        # A new pixel colour!
        if groupCount == 0:
            # First pixel of the image; record it
            lastPixel = pixel
            continue
        if groupCount > 1:
            if currentUniques > 0:
                # We just ended a run of unique pixels. Terminate it, output it.
                print(f"> {currentUniques}\t unique pixels ready - needs pixel count but no RLE repeat flag")
                cmdBlock = "0" + binary_repr(currentUniques, 7)
                print(f"Bitstream: Command block {cmdBlock} then {currentUniques} unique pixels follow:{uniqueOutput}")
                uniqueOutput = ""
                currentUniques = 0
                continue
            # We just ended a run of the same pixels. Terminate it, output it
            print(f"> {groupCount}\t repeat pixels ready - needs pixel count and RLE repeat flag")
            while groupCount > 127:
                # Make sure we don't overflow
                groupCount = groupCount - 127
                cmdBlock = "11111111"
                print(f"Bitstream: Command block {cmdBlock} then 127 pixels, all {pixel}")
            if groupCount > 0:
                # Print any remainder now that the 127 blocks are dealt with
                cmdBlock = "1" + binary_repr(groupCount, 7)
                print(f"Bitstream: Command block {cmdBlock} then {groupCount} pixels, all {pixel}")
        else:
            # This is a unique pixel; start a run of uniques
            currentUniques = currentUniques + 1
            uniqueOutput = f"{uniqueOutput} {pixel}"
        groupCount = 0

# to do: construct bitstream; the above human-readable output appears correct