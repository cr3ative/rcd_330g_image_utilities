#!/usr/bin/env python3
import struct
from PIL import Image

def encode_rle_command(is_compressed, pixel_count):
    """Encode RLE command byte"""
    # Pixel count is stored as count-1 (0-127 range for 1-128 pixels)
    count_bits = pixel_count - 1
    if count_bits > 127:
        raise ValueError(f"Too many pixels in run: {pixel_count} (max 128)")
    
    if is_compressed:
        # Set MSB to 1 for compressed
        command = 0x80 | count_bits
    else:
        # MSB is 0 for uncompressed
        command = count_bits
    
    return command

def compress_rgba_data(rgba_data):
    """Compress RGBA data using RLE compression"""
    if len(rgba_data) % 4 != 0:
        raise ValueError("RGBA data length must be multiple of 4")
    
    compressed = bytearray()
    i = 0
    
    while i < len(rgba_data):
        # Get current pixel
        current_pixel = rgba_data[i:i+4]
        run_length = 1
        
        # Check how many consecutive identical pixels we have
        j = i + 4
        while j < len(rgba_data) and run_length < 128:
            if rgba_data[j:j+4] == current_pixel:
                run_length += 1
                j += 4
            else:
                break
        
        # Decide whether to use RLE compression
        if run_length >= 3:  # Compress runs of 3 or more
            # Write compressed run
            while run_length > 0:
                current_run = min(run_length, 128)
                command = encode_rle_command(True, current_run)
                compressed.append(command)
                compressed.extend(current_pixel)
                run_length -= current_run
        else:
            # Write uncompressed pixels
            # Look ahead to see how many non-repeating pixels we have
            uncompressed_count = 1
            k = i + 4
            
            while k < len(rgba_data) and uncompressed_count < 128:
                next_pixel = rgba_data[k:k+4]
                
                # Check if next pixel starts a run of 3+
                consecutive = 1
                for l in range(k + 4, min(len(rgba_data), k + 12), 4):
                    if rgba_data[l:l+4] == next_pixel:
                        consecutive += 1
                    else:
                        break
                
                if consecutive >= 3:
                    break  # Stop uncompressed run, let RLE handle the repetition
                
                uncompressed_count += 1
                k += 4
            
            # Write uncompressed run
            command = encode_rle_command(False, uncompressed_count)
            compressed.append(command)
            
            for p in range(uncompressed_count):
                pixel_offset = i + (p * 4)
                compressed.extend(rgba_data[pixel_offset:pixel_offset+4])
            
            i = k
            continue
        
        i = j
    
    return compressed

def convert_directory(directory_path, output_directory, file_pattern="*.png"):
    """Convert all PNG files in a directory to OVG format"""
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
            output_name = f"{base_name}.bin"
            output_path = os.path.join(output_directory, output_name)
            
            if png_to_ovg(file_path, output_path):
                success_count += 1
        except Exception as e:
            print(f"✗ Failed to convert {file_path}: {e}")
    
    print(f"\n✅ Successfully converted {success_count}/{len(files)} files")
    return success_count > 0

def png_to_ovg(png_file, ovg_file, format_type="auto"):
    """Convert PNG file to OVG format"""
    print(f"Converting {png_file} -> {ovg_file}")
    
    # Load PNG image
    try:
        image = Image.open(png_file)
        
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        width, height = image.size
        print(f"Image dimensions: {width}x{height}")
        
        # Get raw RGBA data
        rgba_data = image.tobytes('raw', 'RGBA')
        print(f"Raw RGBA data: {len(rgba_data)} bytes ({len(rgba_data)//4} pixels)")
        
        # Determine output format
        if format_type == "auto":
            # Check if dimensions suggest raw RGBA format
            import math
            pixels = len(rgba_data) // 4
            side = int(math.sqrt(pixels))
            if side * side == pixels or (side * (side + 1)) == pixels or ((side + 1) * side) == pixels:
                if pixels < 4000:  # Small images likely to be raw RGBA
                    format_type = "raw_rgba"
                else:
                    format_type = "rle"
            else:
                format_type = "rle"
        
        if format_type == "raw_rgba":
            # Write raw RGBA data directly
            print(f"Output format: raw RGBA")
            with open(ovg_file, 'wb') as f:
                f.write(rgba_data)
            print(f"✓ Created {ovg_file} (raw RGBA)")
        else:
            # Compress using RLE
            print(f"Output format: RLE compressed")
            compressed_data = compress_rgba_data(rgba_data)
            print(f"Compressed data: {len(compressed_data)} bytes")
            print(f"Compression ratio: {len(rgba_data)/len(compressed_data):.2f}:1")
            
            # Write OVG file
            with open(ovg_file, 'wb') as f:
                f.write(compressed_data)
            print(f"✓ Created {ovg_file} (RLE compressed)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error converting {png_file}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_roundtrip(ovg_file=None):
    """Test the roundtrip conversion (OVG->PNG->OVG)"""
    if ovg_file is None:
        ovg_file = "opt/gresfiles/img_off_clock_face_ovg.bin"
    
    print(f"Testing roundtrip conversion with {ovg_file}...")
    
    # First decode original OVG
    import subprocess
    import os
    
    temp_png = "temp_roundtrip_test.png"
    temp_ovg = "temp_roundtrip_test.bin"
    
    print("Step 1: Decoding OVG to PNG...")
    result = subprocess.run(["python3", "ovg_to_png.py", ovg_file, temp_png], capture_output=True, text=True)
    
    if os.path.exists(temp_png):
        print("Step 2: Encoding PNG back to OVG...")
        if png_to_ovg(temp_png, temp_ovg):
            print("Step 3: Comparing file sizes...")
            
            original_size = os.path.getsize(ovg_file)
            roundtrip_size = os.path.getsize(temp_ovg)
            
            print(f"Original OVG: {original_size} bytes")
            print(f"Roundtrip OVG: {roundtrip_size} bytes")
            print(f"Size difference: {roundtrip_size - original_size} bytes ({((roundtrip_size/original_size-1)*100):+.1f}%)")
            
            # Clean up temp files
            os.remove(temp_png)
            os.remove(temp_ovg)
        else:
            print("Failed to encode PNG back to OVG")
    else:
        print("Failed to decode OVG to PNG")

if __name__ == "__main__":
    import sys
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Convert PNG files to OVG format')
    parser.add_argument('input', help='Input PNG file or directory path')
    parser.add_argument('output', nargs='?', help='Output OVG file path (for single file) or use --output-dir for directories')
    parser.add_argument('--output-dir', help='Output directory (required when input is a directory)')
    parser.add_argument('--pattern', default='*.png', help='File pattern for directory conversion (default: *.png)')
    parser.add_argument('--format', choices=['auto', 'rle', 'raw_rgba'], default='auto', 
                       help='Output format: auto (default), rle, or raw_rgba')
    parser.add_argument('--test', action='store_true', help='Test roundtrip conversion')
    
    # Handle the case where no arguments are provided
    if len(sys.argv) == 1:
        print("PNG to OVG Converter")
        print("\nUsage:")
        print("  python3 png_to_ovg.py input.png [output.bin]")
        print("  python3 png_to_ovg.py input.png  # Auto-generate output name")
        print("  python3 png_to_ovg.py input_directory --output-dir output_directory")
        print("  python3 png_to_ovg.py --test [file.bin]  # Test roundtrip conversion")
        print("\nOptions:")
        print("  --output-dir DIR      Output directory (required for directory input)")
        print("  --pattern PATTERN     File pattern for directory conversion (default: *.png)")
        print("  --format FORMAT       Output format: auto (default), rle, or raw_rgba")
        print("  --test                Test roundtrip conversion")
        print("\nExamples:")
        print("  # Single file conversion")
        print("  python3 png_to_ovg.py my_clock.png clock_new.bin")
        print("  python3 png_to_ovg.py clock_face_decoded.png")
        print("  # Directory conversion")
        print("  python3 png_to_ovg.py decoded_images --output-dir new_ovg_files")
        print("  python3 png_to_ovg.py png_dir --output-dir ovg_dir --pattern '*clock*.png'")
        print("  # Testing")
        print("  python3 png_to_ovg.py --test opt/gresfiles/img_off_clock_face_ovg.bin")
        sys.exit(0)
    
    # Handle special case for test mode with old syntax
    if len(sys.argv) >= 2 and sys.argv[1] == "test":
        if len(sys.argv) >= 3:
            test_roundtrip(sys.argv[2])
        else:
            test_roundtrip()
        sys.exit(0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle test mode
    if args.test:
        if args.output:
            test_roundtrip(args.output)
        else:
            test_roundtrip()
        sys.exit(0)
    
    # Check if input is a directory
    if os.path.isdir(args.input):
        # Directory conversion
        if not args.output_dir:
            print("Error: --output-dir is required when input is a directory")
            sys.exit(1)
        
        convert_directory(args.input, args.output_dir, args.pattern)
    else:
        # Single file conversion
        if args.output_dir:
            print("Warning: --output-dir ignored for single file conversion")
        
        if args.output:
            # Explicit output filename
            png_to_ovg(args.input, args.output, args.format)
        else:
            # Auto-generate output filename
            base_name = os.path.splitext(args.input)[0]
            ovg_file = f"{base_name}.bin"
            png_to_ovg(args.input, ovg_file, args.format)