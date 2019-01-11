#!/bin/sh
#created by mengxp
echo before_app_update
echo "Flashing new logo to mtd5..."
dd if=/sysupdate/system/script/logo.bin of=/dev/mtdblock5
echo "Done..."

