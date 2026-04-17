import imagej
import scyjava
from pathlib import Path
import os
import csv


def initialize_imagej():
    """
    Initialize ImageJ with Fiji.
    
    Returns:
        ij: ImageJ instance
    """
    try:
        # Increase heap size for large image stacks before starting Fiji
        scyjava.config.add_option('-Xmx25g')
        scyjava.config.add_option('-Xms25g')
        ij = imagej.init('sc.fiji:fiji:2.14.0', mode='headless')
        print("ImageJ/Fiji initialized successfully with 25GB heap")
        return ij
    except Exception as e:
        print(f"Error initializing ImageJ: {e}")
        raise


def run_fiji_evaluation(image_dir, output_dir=None):
    """
    Execute FIJI macro workflow on converted JPEG images.
    
    Workflow:
    1. Load images from Picture_00s_JPG and Picture_10s_JPG folders
    2. Smooth both image stacks
    3. Subtract 10s from 00s
    4. Invert the result
    5. Apply threshold and convert to mask
    
    Args:
        image_dir (str): Directory containing Picture_00s_JPG and Picture_10s_JPG subfolders
        output_dir (str, optional): Directory to save results. If None, saves in image_dir
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ij = initialize_imagej()
        
        # Set output directory
        if output_dir is None:
            output_dir = image_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Define folder paths
        folder_00s = os.path.join(image_dir, "Picture_00s_JPG")
        folder_10s = os.path.join(image_dir, "Picture_10s_JPG")
        
        # Validate folders exist
        if not os.path.exists(folder_00s):
            print(f"Error: {folder_00s} does not exist")
            return False
        if not os.path.exists(folder_10s):
            print(f"Error: {folder_10s} does not exist")
            return False
        
        print(f"Loading images from {folder_00s}")
        print(f"Loading images from {folder_10s}")
        
        # Check if folders contain images
        jpg_files_00s = [f for f in os.listdir(folder_00s) if f.lower().endswith('.jpg')]
        jpg_files_10s = [f for f in os.listdir(folder_10s) if f.lower().endswith('.jpg')]
        print(f"Found {len(jpg_files_00s)} JPG files in 00s folder")
        print(f"Found {len(jpg_files_10s)} JPG files in 10s folder")
        
        if len(jpg_files_00s) == 0 or len(jpg_files_10s) == 0:
            print("Error: No JPG files found in one or both folders")
            return False
        
        # Open image folders using ImageJ
        # Using FolderOpener directly for reliable stack opening in headless mode
        IJ = scyjava.jimport('ij.IJ')
        FolderOpener = scyjava.jimport('ij.plugin.FolderOpener')
        ImagePlus = scyjava.jimport('ij.ImagePlus')
        WindowManager = scyjava.jimport('ij.WindowManager')
        ImageCalculator = scyjava.jimport('ij.plugin.ImageCalculator')
        Prefs = scyjava.jimport('ij.Prefs')
        
        # Open images using FolderOpener directly (more reliable than IJ.run commands)
        print("Opening first image stack (00s)...")
        fo1 = FolderOpener()
        imp1 = fo1.openFolder(folder_00s)
        if imp1 is None:
            print(f"Error: Could not open images from {folder_00s}")
            return False
        print(f"Successfully opened {imp1.getTitle()} with {imp1.getStackSize()} slices")
        imp1.setTitle("Picture_00s_JPG")
        
        print("Opening second image stack (10s)...")
        fo2 = FolderOpener()
        imp2 = fo2.openFolder(folder_10s)
        if imp2 is None:
            print(f"Error: Could not open images from {folder_10s}")
            return False
        print(f"Successfully opened {imp2.getTitle()} with {imp2.getStackSize()} slices")
        imp2.setTitle("Picture_10s_JPG")
        
        # Verify both stacks have the same number of slices
        slices_00s = imp1.getStackSize()
        slices_10s = imp2.getStackSize()
        if slices_00s != slices_10s:
            print(f"Error: Stack size mismatch! 00s has {slices_00s} slices, 10s has {slices_10s} slices")
            print("Both folders must contain the same number of images")
            return False
        
        # Smooth both stacks
        print("Applying Smooth filter to both stacks...")
        IJ.run(imp1, "Smooth", "stack")
        IJ.run(imp2, "Smooth", "stack")
        
        # Perform image subtraction (imp1 - imp2)
        print("Subtracting 10s from 00s...")
        ic = ImageCalculator()
        imp3 = ic.run("Subtract create stack", imp1, imp2)
        imp3.setTitle("Subtracted")
        
        # Invert the result
        print("Inverting image...")
        IJ.run(imp3, "Invert", "stack")
        
        # Apply threshold and convert to mask
        print("Applying threshold and converting to mask...")
        # Set auto threshold
        IJ.setAutoThreshold(imp3, "Default")
        # Set threshold range
        IJ.setThreshold(imp3, 0, 230)
        # Set black background option
        Prefs.blackBackground = False
        IJ.run(imp3, "Convert to Mask", "method=Default background=Light stack")
        
# Analyze particles per slice and create summary table
        print("Analyzing particles per slice...")
        Analyzer = scyjava.jimport('ij.plugin.filter.Analyzer')
        RoiManager = scyjava.jimport('ij.plugin.frame.RoiManager')
        ImageStack = scyjava.jimport('ij.ImageStack')
        ImageProcessor = scyjava.jimport('ij.process.ImageProcessor')
        ResultsTable = scyjava.jimport('ij.measure.ResultsTable')

        # Get the stack from the processed image
        stack = imp3.getStack()
        n_slices = stack.getSize()

        # Prepare summary data collection
        summary_data = []

        # Process each slice individually
        for slice_idx in range(1, n_slices + 1):  # ImageJ slices are 1-indexed
            # Get the slice name (this should match the original file names)
            slice_label = stack.getSliceLabel(slice_idx)
            if slice_label is None or slice_label == "":
                slice_label = f"Slice_{slice_idx:05d}"

            # Extract this slice as a single image
            slice_ip = stack.getProcessor(slice_idx)
            slice_imp = ImagePlus(slice_label, slice_ip)

            # Clear any previous results
            IJ.run("Clear Results", "")

            # Analyze particles on this slice
            IJ.run(slice_imp, "Analyze Particles...", "display exclude clear")

            # Get results for this slice
            results = ResultsTable.getResultsTable()
            if results is not None:
                particle_count = results.size()
                total_area = 0.0
                total_mean = 0.0

                for i in range(particle_count):
                    try:
                        area = results.getValue("Area", i)
                        mean_val = results.getValue("Mean", i)
                        total_area += area
                        total_mean += mean_val
                    except:
                        pass

                # Calculate summary statistics
                avg_size = total_area / particle_count if particle_count > 0 else 0
                avg_mean = total_mean / particle_count if particle_count > 0 else 0

                # Calculate %Area (area relative to total image area)
                # Assuming 8-bit images, total pixels = width * height
                width = slice_ip.getWidth()
                height = slice_ip.getHeight()
                total_pixels = width * height
                percent_area = (total_area / total_pixels) * 100 if total_pixels > 0 else 0

                # Add to summary data
                summary_data.append({
                    'Slice': slice_label,
                    'Count': particle_count,
                    'Total Area': round(total_area, 3),
                    'Average Size': round(avg_size, 3),
                    '%Area': round(percent_area, 3),
                    'Mean': round(avg_mean, 3)
                })

            # Close the slice image to free memory
            slice_imp.close()

        # Save summary data as CSV
        print("Saving particle analysis summary...")
        csv_path = os.path.join(output_dir, "Particle_Analysis_Results.csv")

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['Slice', 'Count', 'Total Area', 'Average Size', '%Area', 'Mean'])
            # Write data rows
            for row in summary_data:
                writer.writerow([
                    row['Slice'],
                    row['Count'],
                    row['Total Area'],
                    row['Average Size'],
                    row['%Area'],
                    row['Mean']
                ])

        print(f"Summary table saved to {csv_path}")
        print(f"Total slices processed: {len(summary_data)}")
        
        print(f"FIJI evaluation completed successfully!")
        print(f"Results saved to:")
        print(f"  - CSV: {os.path.join(output_dir, 'Particle_Analysis_Results.csv')}")
        
        # Close images to free memory
        imp1.close()
        imp2.close()
        imp3.close()
        
        return True
        
    except Exception as e:
        print(f"Error during FIJI evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        image_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        run_fiji_evaluation(image_dir, output_dir)
    else:
        print("Usage: python fiji_eval.py <image_directory> [output_directory]")