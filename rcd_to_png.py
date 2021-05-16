from PIL import Image

# RCD330 logo.bin format is raw pixel data, 8-bit RGB, in BGRX order.
# The dimensions are 800 wide and 480 high.

in_file = open("logo.bin", "rb")  # opening for [r]eading as [b]inary
data = in_file.read() 
img = Image.frombytes('RGB', (800, 480), data, 'raw', 'BGRX')
output = "logo.png"
img.save(output)
print(output + ' saved')
