# RCD330 Image Utilities

To run these, you need Pillow and numpy. Install via pip:

`pip install Pillow numpy`

## Tools

### Boot logos

* To convert an RCD `logo.bin` file to PNG, edit and run `python3 rcd_to_png.py`
* To convert any 800x480 PNG to RCD `logo.bin`, run `python3 png_to_rcd.py`

I haven't yet flashed any results to my personal RCD330. This is a work in progress, but the BIN conversion works both ways and matches exactly the expected format.

- Credit to `mengxp` for the original image update tarball and conversion utility.
- Credit to @tef and @marksteward for helping me understand XORs!

### OVG bin files (flags, etc)

* To convert an `_ovg.bin` file to PNG, edit and run `python3 ovg_to_png.py`
* There's currently no converter from PNG to `_ovg.bin` format, but now that the RLE compression flags are understood, I can do this soon. Or you can! Submit a PR ;)

- Credit to `Niklas_1414` for pushing me to examine these files. Further credits in the python file.

Cheers!
