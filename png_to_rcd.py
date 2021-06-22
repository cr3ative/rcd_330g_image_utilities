from PIL import Image 
import numpy as np
import operator
import functools

# RCD330 logo.bin format is raw pixel data, 8-bit RGB, in BGRX order.
# The dimensions are 800 wide and 480 high.
# A 3-bit checksum is appended; details are below.

# import image
img = Image.open('logo.png')

# cast to RGBA
data = np.array(img.convert("RGBA"))
r, g, b, a = data.T

# xor all blue pixels together
chksumBlue = functools.reduce(operator.xor, np.array([b]).transpose().flatten())
# and green
chksumGreen = functools.reduce(operator.xor, np.array([g]).transpose().flatten())
# and red
chksumRed = functools.reduce(operator.xor, np.array([r]).transpose().flatten())
# and alpha
chksumAlpha = functools.reduce(operator.xor, np.array([a]).transpose().flatten())

# img output
data = np.array([b, g, r, a])
bgrData = data.transpose()
bgrArray = bgrData.flatten()

f = open('./output.bin', 'wb')
# B G R A ordered data
f.write(bgrArray)
# pixel checksums
f.write(chksumBlue)
f.write(chksumGreen)
f.write(chksumRed)
f.write(chksumAlpha)
f.close()

print('output.bin saved')
