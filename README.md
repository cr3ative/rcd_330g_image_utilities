# RCD330 Logo Utilities

Do you have a Noname (Linux) RCD330G? Do you want a custom boot logo? I might be able to help!

Tested on macOS with Python 2.7.15 (default)

To run these, first run:

`pip install Pillow`

Then to convert RCD `logo.bin` file to PNG, run `rcd_to_png.py`

To convert any 800x480 PNG to RCD `logo.bin`, run `png_to_rcd.py`

The included folder `std_plus_pss-6.5inch_logo_vw_orig.tar` contains the default logo, which is a useful example of an example update tarball created by `mengxp`. You can swap the logo.bin out using your favourite `.tar` creating utility.

Be warned: This process writes raw block-level data to the firmware of your radio. There's a very realistic chance you'll brick your unit with this, and I take no responsibility for it. It's up to you if you rely on this code or not.

I haven't yet flashed any results to my personal RCD330. This is a work in progress.

Currently, we are not generating equal MD5s for files which are meant to be the same:

```[paulcurry@cr3 ~/Desktop/rcd_330g_logo_utilities](master)$ md5 logo.bin
MD5 (logo.bin) = 7996a73f577f6d7847c37bb34bc70995
[paulcurry@cr3 ~/Desktop/rcd_330g_logo_utilities](master)$ md5 output.bin
MD5 (output.bin) = e5574df1f912f97bdd4daa357fcbfd16
```

Credit to `mengxp` for the original image update tarball and bravely discovering mtdblock5.
Credit to `priZrakinside` via https://www.drive2.com/b/518351288971298058/ for the Visteon dump, and for `logo.exe`.

So let's not flash these to units just yet. ;)

Cheers!
