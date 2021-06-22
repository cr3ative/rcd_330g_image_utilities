from PIL import Image
from numpy import binary_repr

# Sources used:
#
# https://reverseengineering.stackexchange.com/questions/27688/open-unknown-image-format-probably-a-raw-image
# Ian correctly identified 32-bpp RGBA, but the description of the "tag block" was confusing
#
# https://www.nxp.com.cn/docs/en/application-note/AN4339.pdf
# Describes command block and RLE routine

# variables; adjust me
filename = "example_bins/ops_ovg.bin"
width = 172
# height automatically calculated

# First, deal with RLE compression as defined by the NXP PDF above

bytesOut = bytearray()
file = open(filename, "rb")  # opening for [r]eading as [b]inary
# Read out the command block (1 byte)
cmd = file.read(1)
while cmd:
    # Take the byte and represent it as a binary string because I'm an idiot and that's easier
    cmd_bin = binary_repr(ord(cmd), 8)
    # Read the most significant binary bit to see what the RLE is up to
    compression_flag = cmd_bin[0]
    # 1 is compressed
    # 0 is single pixel
    if (compression_flag == "1"):
        # print(f"Following data is compressed {compression_flag}")
        # print(f"Compressed pixels which follow: {cmd_bin[1:8]}")
        pixels = (int(cmd_bin[1:8], 2) + 1)
        # print(f"So, {pixels} pixels of the same data - which is the next 4 bytes.")
        rPixel = ord(file.read(1))
        gPixel = ord(file.read(1))
        bPixel = ord(file.read(1))
        aPixel = ord(file.read(1))
        for x in range(pixels):
            bytesOut.append(rPixel)
            bytesOut.append(gPixel)
            bytesOut.append(bPixel)
            bytesOut.append(aPixel)
            # print(f"{pixels} pixels of [{rPixel}, {gPixel}, {bPixel}, {aPixel}] added to the array.")
        # Read next command block
        cmd = file.read(1)
    else:
        # print(f"Uncompressed stream follows -- {compression_flag}")
        pixels = (int(cmd_bin[1:8], 2) + 1)
        # print(f"So, {pixels} pixels to read out as RR GG BB AA")
        for x in range(pixels):
            rPixel = ord(file.read(1))
            gPixel = ord(file.read(1))
            bPixel = ord(file.read(1))
            aPixel = ord(file.read(1))
            bytesOut.append(rPixel)
            bytesOut.append(gPixel)
            bytesOut.append(bPixel)
            bytesOut.append(aPixel)
            # print(f"1 pixel of [{rPixel}, {gPixel}, {bPixel}, {aPixel}] added to the array.")
        # Read next command block
        cmd = file.read(1)

totalPixels = int(len(bytesOut) / 4)
print(f"Image data contains {totalPixels} pixels")
height = int(totalPixels / width)
print(f"Calculated as {width}x{height}")

# Cast RGBX byte stream to image using Pillow
image = Image.frombytes('RGBA', (width, height), bytes(bytesOut), 'raw', 'RGBA')

output = "ovg.png"
image.save(output)
print(output + ' saved')

# Enable the block below to do fast image size discovery; tweak the range
# Open the image in an auto refreshing viewer and hit enter until it looks coherent
if (False):

    for autoWidth in range(440, 500, 1):
        # Generate at given width
        autoHeight = int(totalPixels / autoWidth)
        image = Image.frombytes('RGBA', (autoWidth, autoHeight), bytes(bytesOut), 'raw', 'RGBA')
        output = "ovg.png"
        image.save(output)
        input(f"Saved at {autoWidth} x {autoHeight} - press enter to continue...")