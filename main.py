import os
import sys
import argparse
from PIL import Image
import re

def parse_filename(filename):
    """
    Parse the filename to extract the subfolder name.
    Assumes format: TimeXXXXX_WellXXXX_PointXXXX_TimeXXXXX_SeqXXXX.tif
    Returns the second TimeXXXXX as subfolder name.
    """
    # Remove extension
    name = os.path.splitext(filename)[0]
    parts = name.split('_')
    if len(parts) >= 4:
        return parts[3]  # Second TimeXXXXX
    else:
        return 'unknown'

def convert_tif_to_jpeg(source_dir, dest_dir):
    """
    Convert all .tif files in source_dir to JPEG and save in subfolders based on filename pattern.
    """
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                filepath = os.path.join(root, file)
                subfolder = parse_filename(file)
                subfolder_path = os.path.join(dest_dir, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)
                
                # Convert to JPEG
                try:
                    with Image.open(filepath) as img:
                        # Debug: Print image info
                        print(f"Image mode: {img.mode}, Size: {img.size}, Format: {img.format}")
                        
                        # Handle 16-bit grayscale images
                        if img.mode == 'I;16':
                            # Debug: Check the actual range of values
                            img_array = list(img.getdata())
                            min_val = min(img_array)
                            max_val = max(img_array)
                            print(f"16-bit range: min={min_val}, max={max_val}")
                            
                            # Apply contrast stretching to use full 8-bit range
                            if max_val > min_val:
                                img = img.point(lambda x: (x - min_val) / (max_val - min_val) * 255)
                            else:
                                img = img.point(lambda x: 0)  # All pixels same value
                            img = img.convert('L')
                        elif img.mode == 'L':
                            # Already 8-bit grayscale, save as-is
                            pass
                        elif img.mode == 'LA':
                            # Grayscale with alpha - drop alpha channel
                            img = img.convert('L')
                        elif img.mode == 'P':
                            # Palette mode - convert to grayscale
                            img = img.convert('L')
                        else:
                            # Convert any other mode to grayscale
                            img = img.convert('L')
                        
                        jpeg_filename = os.path.splitext(file)[0] + '.jpg'
                        jpeg_filepath = os.path.join(subfolder_path, jpeg_filename)
                        img.save(jpeg_filepath, 'JPEG', quality=95)
                        print(f"Converted {filepath} to {jpeg_filepath}")
                except Exception as e:
                    print(f"Error converting {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Convert .tif files to JPEG and organize into subfolders.')
    parser.add_argument('source_dir', help='Source directory containing .tif files')
    parser.add_argument('dest_dir', help='Destination directory for JPEG files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Source directory {args.source_dir} does not exist.")
        sys.exit(1)
    
    convert_tif_to_jpeg(args.source_dir, args.dest_dir)
    print("Conversion complete.")

if __name__ == "__main__":
    main()
