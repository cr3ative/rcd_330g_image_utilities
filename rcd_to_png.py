from PIL import Image

# Created by Paul Curry / @cr3
# Huge thanks to 4pda.ru for the pointers
# RCD330 logo.bin format is raw pixel data, 8-bit RGB, in BGRX order.
# The dimensions are 800 wide and 480 high.

# Requires PIL, use 'pip install Pillow' to get it

# Your file should be called logo.bin
# Then run 'python rcd_to_png.py'
# We will create logo.png :)

in_file = open("logo.bin", "rb")  # opening for [r]eading as [b]inary
data = in_file.read() 
img = Image.frombytes('RGB', (800, 480), data, 'raw', 'BGRX')
output = "logo.png"
img.save(output)
print(output + ' saved')
