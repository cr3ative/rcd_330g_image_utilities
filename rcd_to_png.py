from PIL import Image

# RCD330 logo.bin format is raw pixel data, 8-bit RGB, in BGRX order.
# The dimensions are 800 wide and 480 high.

# variables; adjust me
filename = "example_bins/logo.bin"
width = 800
height = 480

# let's go!
in_file = open(filename, "rb")  # opening for [r]eading as [b]inary
data = in_file.read() 
img = Image.frombytes('RGBA', (width, height), data, 'raw', 'BGRA')
output = "logo.png"
img.save(output)
print(output + ' saved')
