# RCD330 Logo Utilities

Do you have a Noname (Linux) RCD330G? Do you want a custom boot logo? I might be able to help!

Tested on macOS with Python 2.7.15 (default)

To run these, first run:

`pip install Pillow`

Then to convert RCD `logo.bin` file to PNG, run `rcd_to_png.py`
To convert any 800x480 PNG to RCD `logo.bin`, run `png_to_rcd.py`

I haven't yet flashed any results to my personal RCD330. This is a work in progress, but the BIN conversion works both ways and matches exactly the expected format.

- Credit to `mengxp` for the original image update tarball and conversion utility.
- Credit to @tef and @marksteward for helping me understand XORs!

Cheers!
