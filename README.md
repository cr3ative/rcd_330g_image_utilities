# RCD330 Image Utilities

Python 3 only because who uses 2 any more? Nerds, that's who. To run these, you need Pillow and numpy. Install via pip:

`pip install Pillow numpy`

## Tools

### Boot logos

* To convert an RCD `logo.bin` file to a PNG called `logo.png`, edit and run `python3 rcd_to_png.py`
* To convert any 800x480 PNG called `logo.png` to RCD `logo.bin`, run `python3 png_to_rcd.py`

I haven't yet flashed any results to my personal RCD330. This is a work in progress, but the BIN conversion works both ways and matches exactly the expected format.

- Credit to `mengxp` for the original image update tarball and conversion utility.
- Credit to @tef and @marksteward for helping me understand XORs!

### OVG bin files (flags, etc)

* To convert an `_ovg.bin` file to PNG, edit and run `python3 ovg_to_png.py`
* To convert any PNG to an `_ovg.bin` compatible file, edit and run `python3 png_to_ovg.py`

- Credit to `Niklas_1414` for pushing me to examine these files. Further credits in the python file.

Cheers!
