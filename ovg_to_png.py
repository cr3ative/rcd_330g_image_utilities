#!/usr/bin/env python3
import struct
import math
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Sources used:
#
# https://reverseengineering.stackexchange.com/questions/27688/open-unknown-image-format-probably-a-raw-image
# Ian correctly identified 32-bpp RGBA, but the description of the "tag block" was confusing
#
# https://www.nxp.com.cn/docs/en/application-note/AN4339.pdf
# Describes command block and RLE routine

def binary_repr(value, width):
    """Convert integer to binary string representation"""
    return format(value, f'0{width}b')

def create_bmp_header(width, height, bits_per_pixel=24):
    """Create a BMP file header"""
    row_size = ((width * bits_per_pixel + 31) // 32) * 4
    file_size = 54 + (row_size * height)
    
    bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    dib_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, bits_per_pixel, 0,
                            row_size * height, 2835, 2835, 0, 0)
    return bmp_header + dib_header

def detect_file_format(filename):
    """Detect if file is RLE OVG or raw RGBA format"""
    with open(filename, "rb") as file:
        data = file.read()
        
    if len(data) < 4:
        return "unknown"
    
    # Check if file size is divisible by 4 (RGBA pixels)
    if len(data) % 4 != 0:
        return "rle_ovg"  # Raw RGBA should be divisible by 4
    
    # Check for patterns that suggest raw RGBA
    pixels = len(data) // 4
    
    # Check if it forms a reasonable square or near-square dimension
    import math
    side = int(math.sqrt(pixels))
    if side * side == pixels or (side * (side + 1)) == pixels or ((side + 1) * side) == pixels:
        # Could be raw RGBA if forms reasonable square dimensions
        
        # Check for repeating patterns typical of raw RGBA
        pattern_count = 0
        for i in range(0, min(100, len(data) - 4), 4):
            # Check if RGBA values are reasonable (not RLE command bytes)
            r, g, b, a = data[i:i+4]
            if a in [0, 255]:  # Common alpha values
                pattern_count += 1
        
        if pattern_count >= 10:  # If many pixels have typical alpha values
            return "raw_rgba"
    
    return "rle_ovg"

def decode_ovg_file(filename):
    """Decode OVG file using the RLE format or raw RGBA"""
    
    format_type = detect_file_format(filename)
    print(f"Detected format: {format_type}")
    
    if format_type == "raw_rgba":
        return decode_raw_rgba_file(filename)
    else:
        return decode_rle_ovg_file(filename)

def decode_raw_rgba_file(filename):
    """Decode raw RGBA file"""
    with open(filename, "rb") as file:
        data = file.read()
    
    pixels = len(data) // 4
    print(f"Raw RGBA data contains {pixels} pixels")
    return bytearray(data), pixels

def decode_rle_ovg_file(filename):
    """Decode OVG file using the RLE format"""
    
    bytesOut = bytearray()
    
    with open(filename, "rb") as file:
        # Read out the command block (1 byte)
        cmd = file.read(1)
        
        while cmd:
            # Take the byte and represent it as a binary string
            cmd_bin = binary_repr(ord(cmd), 8)
            # Read the most significant binary bit to see what the RLE is up to
            compression_flag = cmd_bin[0]
            
            # 1 is compressed, 0 is single pixel
            if compression_flag == "1":
                # Compressed pixels
                pixels = (int(cmd_bin[1:8], 2) + 1)
                
                # Read the pixel data (RGBA)
                pixel_data = file.read(4)
                if len(pixel_data) < 4:
                    break
                    
                rPixel, gPixel, bPixel, aPixel = pixel_data
                
                # Add repeated pixels
                for x in range(pixels):
                    bytesOut.append(rPixel)
                    bytesOut.append(gPixel)
                    bytesOut.append(bPixel)
                    bytesOut.append(aPixel)
                
                # Read next command block
                cmd = file.read(1)
            else:
                # Uncompressed stream follows
                pixels = (int(cmd_bin[1:8], 2) + 1)
                
                # Read individual pixels
                for x in range(pixels):
                    pixel_data = file.read(4)
                    if len(pixel_data) < 4:
                        break
                    
                    rPixel, gPixel, bPixel, aPixel = pixel_data
                    bytesOut.append(rPixel)
                    bytesOut.append(gPixel)
                    bytesOut.append(bPixel)
                    bytesOut.append(aPixel)
                
                # Read next command block
                cmd = file.read(1)
    
    totalPixels = int(len(bytesOut) / 4)
    print(f"Image data contains {totalPixels} pixels")
    
    return bytesOut, totalPixels

def create_image_from_rgba(rgba_data, width, height, output_file):
    """Create image file from RGBA data (PNG if PIL available, BMP otherwise)"""
    
    if PIL_AVAILABLE and output_file.endswith('.png'):
        # Create PNG using PIL
        image = Image.frombytes('RGBA', (width, height), bytes(rgba_data), 'raw', 'RGBA')
        image.save(output_file)
        print(f"✓ Created PNG: {output_file}")
    else:
        # Create BMP file
        if output_file.endswith('.png'):
            output_file = output_file.replace('.png', '.bmp')
        
        # Create BMP header
        bmp_header = create_bmp_header(width, height, 24)
        
        # Convert RGBA to BGR (BMP format)
        bgr_data = bytearray()
        for i in range(0, len(rgba_data), 4):
            if i + 3 < len(rgba_data):
                r, g, b, a = rgba_data[i:i+4]
                
                # Handle transparency - blend with white background
                if a < 255:
                    # Alpha blending with white background
                    alpha = a / 255.0
                    r = int(r * alpha + 255 * (1 - alpha))
                    g = int(g * alpha + 255 * (1 - alpha))
                    b = int(b * alpha + 255 * (1 - alpha))
                
                bgr_data.extend([b, g, r])  # BGR format for BMP
        
        # Ensure we have enough data
        expected_size = width * height * 3
        while len(bgr_data) < expected_size:
            bgr_data.extend([0, 0, 0])
        
        # Write BMP file
        row_size = ((width * 24 + 31) // 32) * 4
        padding = row_size - (width * 3)
        
        with open(output_file, 'wb') as f:
            f.write(bmp_header)
            
            # Write rows bottom to top (BMP format)
            for y in range(height - 1, -1, -1):
                row_start = y * width * 3
                row_end = row_start + width * 3
                f.write(bgr_data[row_start:row_end])
                
                # Add padding
                if padding > 0:
                    f.write(b'\x00' * padding)
        
        print(f"✓ Created BMP: {output_file}")

def auto_detect_dimensions(totalPixels, verbose=False):
    """Auto-detect likely image dimensions using multiple strategies"""
    
    # Strategy 1: Perfect square
    side = int(math.sqrt(totalPixels))
    if side * side == totalPixels:
        return side, side
    
    # Strategy 1.5: Near-perfect square (for raw RGBA data)
    if abs(side * side - totalPixels) <= 2 * side:
        # Check if it's close to a square
        if side * (side + 1) == totalPixels:
            return side, side + 1
        elif (side + 1) * side == totalPixels:
            return side + 1, side
    
    # Strategy 2: Find all possible factor pairs
    factors = []
    for i in range(1, int(math.sqrt(totalPixels)) + 1):
        if totalPixels % i == 0:
            width = totalPixels // i
            height = i
            factors.append((width, height, abs(width - height)))  # Include aspect ratio difference
    
    # Strategy 3: Score factor pairs by likelihood
    scored_factors = []
    for width, height, diff in factors:
        score = 0
        
        # Prefer reasonable image sizes (not too thin/wide)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio <= 4:  # Reasonable aspect ratio
            score += 100
        
        # Prefer common resolutions and "nice" numbers
        for dimension in [width, height]:
            if dimension in [160, 200, 240, 256, 320, 400, 480, 640, 800, 1024]:
                score += 20
            if dimension % 8 == 0:  # Divisible by 8 (common for images)
                score += 10
            if dimension % 16 == 0:  # Divisible by 16 (even better)
                score += 5
        
        # Prefer closer to square (but not mandatory)
        if aspect_ratio <= 2:
            score += 30
        elif aspect_ratio <= 1.5:
            score += 50
        
        # Prefer sizes that aren't too small or too large
        if 50 <= min(width, height) <= 1000:
            score += 40
        
        scored_factors.append((score, width, height))
    
    # Sort by score (highest first) and return best match
    if scored_factors:
        scored_factors.sort(reverse=True)
        if verbose:
            print(f"Top dimension candidates:")
            for i, (score, w, h) in enumerate(scored_factors[:5]):
                print(f"  {i+1}. {w}x{h} (score: {score})")
        _, best_width, best_height = scored_factors[0]
        return best_width, best_height
    
    # Strategy 4: Fallback - try common aspect ratios
    for ratio in [(1, 1), (4, 3), (3, 2), (16, 9), (2, 1)]:
        width = int(math.sqrt(totalPixels * ratio[0] / ratio[1]))
        height = totalPixels // width
        if width * height <= totalPixels and width > 0 and height > 0:
            return width, height
    
    # Final fallback
    side = int(math.sqrt(totalPixels))
    return side, totalPixels // side

def discover_image_size(rgba_data, totalPixels, width_min=35, width_max=400, width_step=1):
    """Interactive image size discovery"""
    print(f"\n🔍 Image Size Discovery Mode")
    print(f"Total pixels: {totalPixels}")
    print(f"Testing widths from {width_min} to {width_max} (step: {width_step})")
    print("Press Enter to try next size, 'q' to quit, or type width number to jump to specific size")
    
    current_width = width_min
    
    while current_width <= width_max:
        height = totalPixels // current_width
        
        if height * current_width <= totalPixels:
            # Create test image
            test_filename = f"size_test_{current_width}x{height}.png"
            create_image_from_rgba(rgba_data, current_width, height, test_filename)
            
            print(f"\n📐 Current size: {current_width}x{height}")
            user_input = input(f"Saved as {test_filename} - Press Enter for next size, 'q' to quit, or enter width: ").strip()
            
            if user_input.lower() == 'q':
                print("Size discovery stopped.")
                break
            elif user_input.isdigit():
                new_width = int(user_input)
                if width_min <= new_width <= width_max:
                    current_width = new_width
                    continue
                else:
                    print(f"Width {new_width} out of range ({width_min}-{width_max})")
            
            current_width += width_step
        else:
            current_width += width_step

def convert_directory(directory_path, output_directory, width=None, height=None, verbose=False, file_pattern="*.bin"):
    """Convert all OVG files in a directory"""
    import os
    import glob
    
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a directory")
        return False
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")
    elif not os.path.isdir(output_directory):
        print(f"Error: {output_directory} exists but is not a directory")
        return False
    
    # Find all matching files
    search_pattern = os.path.join(directory_path, file_pattern)
    files = glob.glob(search_pattern)
    
    if not files:
        print(f"No files matching '{file_pattern}' found in {directory_path}")
        return False
    
    print(f"Found {len(files)} files to convert in {directory_path}")
    print(f"Output directory: {output_directory}")
    success_count = 0
    
    for file_path in sorted(files):
        try:
            print(f"\n--- Converting {os.path.basename(file_path)} ---")
            
            # Generate output filename in the output directory
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if width and height:
                output_name = f"{base_name}_decoded_{width}x{height}.png"
            else:
                output_name = f"{base_name}_decoded.png"
            output_path = os.path.join(output_directory, output_name)
            
            if convert_single_file(file_path, output_path, width=width, height=height, verbose=verbose):
                success_count += 1
        except Exception as e:
            print(f"✗ Failed to convert {file_path}: {e}")
    
    print(f"\n✅ Successfully converted {success_count}/{len(files)} files")
    return success_count > 0

def convert_single_file(filename, output_name=None, width=None, height=None, discover_size=False, verbose=False):
    """Convert a single OVG file to PNG"""
    try:
        print(f"Converting {filename}...")
        rgba_data, totalPixels = decode_ovg_file(filename)
        
        if discover_size:
            # Run interactive size discovery
            discover_image_size(rgba_data, totalPixels)
            return True
        
        # Determine dimensions
        if width and height:
            # Use provided dimensions
            print(f"Using specified dimensions: {width}x{height}")
        elif width and not height:
            # Calculate height from width
            height = totalPixels // width
            print(f"Calculated dimensions: {width}x{height}")
        elif height and not width:
            # Calculate width from height
            width = totalPixels // height
            print(f"Calculated dimensions: {width}x{height}")
        else:
            # Auto-detect dimensions using multiple strategies
            width, height = auto_detect_dimensions(totalPixels, verbose=verbose)
            print(f"Auto-detected dimensions: {width}x{height}")
        
        # Generate output filename
        if output_name is None:
            import os
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_name = f"{base_name}_decoded_{width}x{height}.png"
        
        # Create PNG
        create_image_from_rgba(rgba_data, width, height, output_name)
        
        return True
    
    except Exception as e:
        print(f"✗ Error converting {filename}: {e}")
        import traceback
        traceback.print_exc()
        return False



if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert OVG files to PNG format')
    parser.add_argument('input', help='Input OVG file path')
    parser.add_argument('output', nargs='?', help='Output PNG file path (optional)')
    parser.add_argument('-w', '--width', type=int, help='Specify image width')
    parser.add_argument('--height', type=int, help='Specify image height')
    parser.add_argument('-d', '--discover', action='store_true', 
                       help='Interactive size discovery mode')
    parser.add_argument('--width-min', type=int, default=35, 
                       help='Minimum width for discovery (default: 35)')
    parser.add_argument('--width-max', type=int, default=400, 
                       help='Maximum width for discovery (default: 400)')
    parser.add_argument('--width-step', type=int, default=1, 
                       help='Width step for discovery (default: 1)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show dimension detection details')
    parser.add_argument('--pattern', default='*.bin',
                       help='File pattern for directory conversion (default: *.bin)')
    parser.add_argument('--output-dir', 
                       help='Output directory (required when input is a directory)')
    
    # Handle the case where no arguments are provided
    if len(sys.argv) == 1:
        print("OVG to PNG Converter")
        print("\nUsage:")
        print("  python3 ovg_to_png.py input.bin [output.png]")
        print("  python3 ovg_to_png.py input.bin --width 286 --height 286")
        print("  python3 ovg_to_png.py input.bin --discover")
        print("  python3 ovg_to_png.py input_directory --output-dir output_directory")
        print("\nOptions:")
        print("  -w, --width WIDTH     Specify image width")
        print("  --height HEIGHT       Specify image height") 
        print("  -d, --discover        Interactive size discovery mode")
        print("  --output-dir DIR      Output directory (required for directory input)")
        print("  --pattern PATTERN     File pattern for directory conversion (default: *.bin)")
        print("  --width-min MIN       Minimum width for discovery (default: 35)")
        print("  --width-max MAX       Maximum width for discovery (default: 400)")
        print("  --width-step STEP     Width step for discovery (default: 1)")
        print("  -v, --verbose         Show dimension detection details")
        print("\nExamples:")
        print("  # Single file conversion")
        print("  python3 ovg_to_png.py opt/gresfiles/img_off_clock_face_ovg.bin")
        print("  python3 ovg_to_png.py clock.bin my_clock.png --width 200")
        print("  python3 ovg_to_png.py unknown.bin --discover --width-min 50 --width-max 300")
        print("  # Directory conversion")
        print("  python3 ovg_to_png.py opt/gresfiles --output-dir decoded_images")
        print("  python3 ovg_to_png.py input_dir --output-dir output_dir --width 286 --height 286")
        print("  python3 ovg_to_png.py input_dir --output-dir output_dir --pattern '*clock*.bin'")
        sys.exit(0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if input is a directory
    import os
    if os.path.isdir(args.input):
        # Directory conversion
        if not args.output_dir:
            print("Error: --output-dir is required when input is a directory")
            sys.exit(1)
        if args.discover:
            print("Error: Discovery mode is not supported for directory conversion")
            sys.exit(1)
        
        convert_directory(args.input, args.output_dir, args.width, args.height, 
                         args.verbose, args.pattern)
    else:
        # Single file conversion
        if args.output_dir:
            print("Warning: --output-dir ignored for single file conversion")
        
        if args.discover:
            rgba_data, totalPixels = decode_ovg_file(args.input)
            discover_image_size(rgba_data, totalPixels, args.width_min, args.width_max, args.width_step)
        else:
            convert_single_file(args.input, args.output, args.width, args.height, verbose=args.verbose)