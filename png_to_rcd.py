from PIL import Image

# Created by Paul Curry / @cr3
# Huge thanks to 4pda.ru for the pointers
# RCD330 logo.bin format is raw pixel data, 8-bit RGB, in BGRX order.
# The dimensions are 800 wide and 480 high.

# Requires PIL, use 'pip install Pillow' to get it

# Name your PNG input.png
# Then run 'python png_to_rcd.py'
# We will create output.bin :)

img = Image.open('input.png')
img_bytes = img.tobytes("raw", "BGRX")

f = open('./output.bin', 'w')
f.write(img_bytes)
f.close()

print 'output.bin saved'
