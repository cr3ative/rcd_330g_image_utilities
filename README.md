# RCD330 Image Utilities: OVG Image Format Converter

This repository contains tools for converting OVG (proprietary image format) files to PNG and back, specifically designed for car stereo firmware modification.

## Background

OVG files are a proprietary image format used in the RCD330 (and likely other) car stereo firmware. They use RLE (Run-Length Encoding) compression with RGBA color data, saved to a binary file extension.

This project was spun up out of a desire to skin more of the interface than ust the bootlogo. Much credit goes to [@cr3ative](https://github.com/cr3ative/) for sharing his initial discoveries publicly on GitHub in the [RCD 330 Image Utilities repo](https://github.com/cr3ative/rcd_330g_image_utilities).

## File Format Description

The converter supports two different OVG file formats:

### 1. RLE-Compressed OVG Format
The traditional OVG format uses RLE (Run-Length Encoding) compression:
- **Command Block**: 1 byte indicating compression type and pixel count
- **Pixel Data**: RGBA data (4 bytes per pixel)
- **RLE Compression**: Efficient encoding for repeated pixels

### 2. Raw RGBA Format
Some OVG files contain raw RGBA pixel data without compression:
- **Direct RGBA**: 4 bytes per pixel (R, G, B, A)
- **No compression**: Pixel data stored sequentially
- **Square dimensions**: Often forms perfect or near-perfect squares

The converter automatically detects which format is used and processes accordingly.

### RLE Command Block Format (Format 1 only)
```
Bit 7 (MSB): Compression flag (1 = compressed, 0 = uncompressed)
Bits 6-0: Pixel count - 1 (0-127 representing 1-128 pixels)
```

### RLE Compression Types (Format 1 only)
- **Compressed (MSB = 1)**: Next 4 bytes (RGBA) repeated N times
- **Uncompressed (MSB = 0)**: Next N×4 bytes are individual RGBA pixels

### Format Auto-Detection
The converter automatically detects the format by analyzing:
- **File size**: Must be divisible by 4 for raw RGBA
- **Dimensions**: Raw RGBA often forms perfect squares
- **Alpha patterns**: Common alpha values (0, 255) indicate raw RGBA

## Tools Included

### 1. `ovg_to_png.py` - OVG to PNG Decoder
Converts OVG files to PNG format with transparency preservation.

### 2. `png_to_ovg.py` - PNG to OVG Encoder  
Converts PNG files back to OVG format with RLE compression.

## Requirements

```bash
pip3 install --user Pillow
```

## Usage

### Decoding OVG to PNG

#### Basic Conversion
```bash
python3 ovg_to_png.py input.bin [output.png]
```

Examples:
```bash
# Convert with auto-detected dimensions and format
python3 ovg_to_png.py opt/gresfiles/img_off_clock_face_ovg.bin

# Convert with custom output name
python3 ovg_to_png.py opt/gresfiles/img_off_clock_face_ovg.bin my_clock_face.png

# The converter will automatically detect if the file is RLE-compressed or raw RGBA
# Example output:
# Detected format: raw_rgba
# Raw RGBA data contains 1521 pixels
# Auto-detected dimensions: 39x39
```

#### Specify Exact Dimensions
```bash
python3 ovg_to_png.py input.bin output.png --width 286 --height 286
python3 ovg_to_png.py input.bin --width 200  # Height calculated automatically
```

#### Interactive Size Discovery
```bash
# Use size discovery to find correct dimensions
python3 ovg_to_png.py input.bin --discover

# Customize discovery range
python3 ovg_to_png.py input.bin --discover --width-min 50 --width-max 300 --width-step 5
```

The discovery mode will:
- Generate test images at different sizes
- Display each size and wait for your input
- Let you jump to specific widths
- Help you find the correct dimensions visually

#### Available Options
- `-w, --width WIDTH` - Specify image width
- `--height HEIGHT` - Specify image height  
- `-d, --discover` - Interactive size discovery mode
- `--width-min MIN` - Minimum width for discovery (default: 35)
- `--width-max MAX` - Maximum width for discovery (default: 400)
- `--width-step STEP` - Width step for discovery (default: 1)

#### Usage Help
```bash
python3 ovg_to_png.py
```

#### Output Files
- **Clock Face**: 286×286 pixels (perfect square from 81,796 pixels)
- **Clock Shadow**: 400×400 pixels
- **Clock Spotlight**: 619×619 pixels  
- **Clock Hands**: 286×286 pixels each

### Encoding PNG to OVG

#### Convert Specific File
```bash
python3 png_to_ovg.py input.png [output.bin]
```

Examples:
```bash
# Convert with custom output name
python3 png_to_ovg.py my_custom_clock.png img_off_clock_face_ovg_new.bin

# Convert with auto-generated output name (replaces .png with .bin)
python3 png_to_ovg.py clock_face_decoded.png
# Creates: clock_face_decoded.bin
```

#### Usage Help
```bash
python3 png_to_ovg.py
```

Shows usage information and examples.

#### Test Roundtrip Conversion
```bash
# Test with default file
python3 png_to_ovg.py test

# Test with specific file
python3 png_to_ovg.py test opt/gresfiles/img_off_clock_face_ovg.bin
```

This will:
1. Decode the original OVG to PNG
2. Encode the PNG back to OVG  
3. Compare file sizes and report compression efficiency
4. Clean up temporary files automatically

## Complete Workflow for Clock Customization

### Step 1: Extract Original Images
```bash
# Extract specific files with custom names
python3 ovg_to_png.py opt/gresfiles/img_off_clock_face_ovg.bin my_clock_face.png
python3 ovg_to_png.py opt/gresfiles/img_off_clock_shadow_ovg.bin my_shadow.png
python3 ovg_to_png.py opt/gresfiles/img_off_clock_spotlight_ovg.bin my_spotlight.png

# Or extract with auto-generated names
python3 ovg_to_png.py opt/gresfiles/img_off_clock_face_ovg.bin
# Creates: img_off_clock_face_ovg_decoded.png
```

### Step 2: Edit Images
- Open your extracted PNG files in your image editor
- Modify the clock face design as desired
- Edit other components (shadow, spotlight, hands) if needed
- Save as PNG with transparency preserved

### Step 3: Convert Back to OVG
```bash
# Convert specific files with custom output names
python3 png_to_ovg.py my_clock_face.png img_off_clock_face_ovg_new.bin
python3 png_to_ovg.py my_shadow.png img_off_clock_shadow_ovg_new.bin

# Or convert with auto-generated names
python3 png_to_ovg.py img_off_clock_face_ovg_decoded.png
# Creates: img_off_clock_face_ovg_decoded.bin
```

### Step 4: Replace in Firmware
- Backup original files first!
- Replace original `.bin` files with corresponding `*_new.bin` files
- Update firmware with modified files

## Key Files

### Input Files (Original OVG)
- `opt/gresfiles/img_off_clock_face_ovg.bin` - Main clock face
- `opt/gresfiles/img_off_clock_shadow_ovg.bin` - Clock shadow
- `opt/gresfiles/img_off_clock_spotlight_ovg.bin` - Clock spotlight
- `opt/gresfiles/img_off_clock_hour_XX_ovg.bin` - Hour hand positions
- `opt/gresfiles/img_off_clock_minute_XX_ovg.bin` - Minute hand positions
- `opt/gresfiles/img_off_clock_second_XX_ovg.bin` - Second hand positions

### Output Files (Editable PNG)
- `clock_face_decoded.png` - Main clock face (286×286)
- `img_off_clock_*_decoded.png` - Individual components

### Generated Files (New OVG)
- `img_off_clock_face_ovg_new.bin` - Modified clock face
- `img_off_clock_*_ovg_new.bin` - Modified components

## Technical Details

### Compression Performance
Typical compression ratios achieved:
- **Clock Face**: ~2.8:1 compression
- **Clock Shadow**: ~10.8:1 compression  
- **Clock Hands**: ~33-41:1 compression
- **Spotlight**: ~11.3:1 compression

### Image Specifications
- **Format**: RGBA (32-bit with alpha channel)
- **Typical Size**: 286×286 pixels for main components
- **Color Depth**: 8 bits per channel (R, G, B, A)
- **Byte Order**: Standard RGBA pixel ordering

## Troubleshooting

### PIL/Pillow Not Found
```bash
pip3 install --user Pillow
```

### File Not Found Errors
Ensure the `opt/gresfiles/` directory exists with original OVG files.

### Size Mismatch
The converter automatically calculates optimal dimensions and detects file format. If dimensions appear incorrect:

1. **Check format detection**: The converter will show "Detected format: raw_rgba" or "Detected format: rle_ovg"
2. **Raw RGBA files**: Should auto-detect to perfect or near-perfect squares
3. **RLE OVG files**: May require manual dimension specification with `--width` and `--height`
4. **Use discovery mode**: `--discover` to find correct dimensions visually

### Compression Issues
If the generated OVG file is significantly larger than the original:
1. Check for unnecessary transparency in your PNG
2. Ensure solid color areas are truly solid (no noise/gradients)
3. The RLE compression works best with areas of repeated pixels

## Development Notes

### Discovery Process
1. Initial attempts tried standard image formats (BMP, RGB, etc.)
2. Analyzed byte patterns showing 0xFF padding and RLE-like structures  
3. Found reference to NXP AN4339 PDF describing similar RLE format
4. Reverse-engineered the exact command block structure
5. Implemented both decoder and encoder with roundtrip testing

### Format Insights
- Files start with 0xFF padding that should be skipped
- Command blocks use 7-bit pixel counts (1-128 pixels per command)
- RLE compression is very effective for clock graphics with large solid areas
- Alpha channel is preserved and properly handled

## References

- [NXP AN4339 Application Note](https://www.nxp.com.cn/docs/en/application-note/AN4339.pdf) - Describes similar RLE routine
- [Reverse Engineering Stack Exchange](https://reverseengineering.stackexchange.com/questions/27688/open-unknown-image-format-probably-a-raw-image) - Initial format identification

## License

This project is provided as-is for educational and personal use. Always backup original firmware before making modifications.