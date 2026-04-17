import os
import sys
import argparse
from PIL import Image
import re
import imagej
import scyjava
from fiji_eval import run_fiji_evaluation


def parse_filename(filename):
    """
    Parse the filename to extract the subfolder name.
    Assumes format: TimeXXXXX_WellXXXX_PointXXXX_TimeXXXXX_SeqXXXX.tif
    Returns Picture_00s_JPG or Picture_10s_JPG as subfolder name based on the second TimeXXXXX.
    """
    # Remove extension
    name = os.path.splitext(filename)[0]
    parts = name.split('_')
    if len(parts) >= 4:
        if parts[3] == 'Time00000': 
            return 'Picture_00s_JPG'
        elif parts[3] == 'Time00001':
            return 'Picture_10s_JPG'
    else:
        return 'unknown'


def convert_tif_to_jpeg(source_dir, dest_dir):
    """
    Convert all .tif files in source_dir to JPEG and save in subfolders based on filename pattern.
    """
    converted_count = 0
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
                        converted_count += 1
                except Exception as e:
                    print(f"Error converting {filepath}: {e}")
    
    return converted_count


def main():
    parser = argparse.ArgumentParser(
        description='Convert .tif files to JPEG and perform FIJI evaluation.'
    )
    parser.add_argument('source_dir', help='Source directory containing .tif files')
    parser.add_argument('dest_dir', help='Destination directory for JPEG files and results')
    parser.add_argument(
        '--no-fiji',
        action='store_true',
        help='Skip FIJI evaluation and only convert TIF to JPEG'
    )
    parser.add_argument(
        '--fiji-only',
        action='store_true',
        help='Run only FIJI evaluation on existing JPEG folders (skip TIF conversion)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Separate output directory for FIJI results (default: same as dest_dir)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Source directory {args.source_dir} does not exist.")
        sys.exit(1)
    
    # Handle different execution modes
    if args.fiji_only:
        # Run only FIJI evaluation on existing JPEG folders
        print("=" * 60)
        print("Running FIJI evaluation only...")
        print("=" * 60)
        output_dir = args.output_dir if args.output_dir else args.source_dir
        success = run_fiji_evaluation(args.source_dir, output_dir)
        
        if success:
            print("\n" + "=" * 60)
            print("FIJI EVALUATION COMPLETE!")
            print("=" * 60)
            print(f"Results saved to: {output_dir}")
        else:
            print("\nFIJI evaluation failed. Check error messages above.")
            sys.exit(1)
    else:
        # Step 1: Convert TIF to JPEG
        print("=" * 60)
        print("STEP 1: Converting TIF files to JPEG...")
        print("=" * 60)
        converted_count = convert_tif_to_jpeg(args.source_dir, args.dest_dir)
        print(f"\nConversion complete. {converted_count} files converted.\n")
        
        # Step 2: Run FIJI evaluation (unless skipped)
        if not args.no_fiji:
            print("=" * 60)
            print("STEP 2: Running FIJI evaluation...")
            print("=" * 60)
            output_dir = args.output_dir if args.output_dir else args.dest_dir
            success = run_fiji_evaluation(args.dest_dir, output_dir)
            
            if success:
                print("\n" + "=" * 60)
                print("WORKFLOW COMPLETE!")
                print("=" * 60)
                print(f"JPEG files saved to: {args.dest_dir}")
                print(f"FIJI results saved to: {output_dir}")
            else:
                print("\nFIJI evaluation failed. Check error messages above.")
                sys.exit(1)
        else:
            print("\nFIJI evaluation skipped (--no-fiji flag set).")
            print(f"JPEG files saved to: {args.dest_dir}")


if __name__ == "__main__":
    main()
