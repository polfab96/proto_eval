# Proto Eval

An automated image analysis workflow that converts .tif files to JPEG format and performs automated FIJI/ImageJ evaluation for motility assay analysis.

## Workflow

The script automates a complete two-step workflow:

1. **TIF to JPEG Conversion**: Converts 16-bit TIF files to 8-bit JPEG with automatic contrast stretching and organizes them into subfolders (`Picture_00s_JPG` and `Picture_10s_JPG`) based on filename patterns.

2. **FIJI Evaluation**: Uses ImageJ/Fiji to process the converted images:
   - Loads image stacks from both time points
   - Applies Smooth filter to reduce noise
   - Subtracts the 10s time point from the 00s time point
   - Inverts the result
   - Applies threshold and converts to binary mask
   - Analyzes particles and generates results table
   - Saves results as CSV for further analysis

## Usage

### Basic Usage (Full Automated Workflow)

Run the script with source and destination directories:

```bash
python main.py "/path/to/source/tif" "/path/to/output"
```

### Command-Line Options

- `--no-fiji`: Skip FIJI evaluation and only convert TIF to JPEG
  ```bash
  python main.py "/path/to/source" "/path/to/output" --no-fiji
  ```

- `--fiji-only`: Run only FIJI evaluation on existing JPEG folders (skip TIF conversion)
  ```bash
  python main.py "/path/to/jpeg_folders" "/path/to/results" --fiji-only
  ```

  *Note: The source directory must contain the `Picture_00s_JPG` and `Picture_10s_JPG` subfolders.*

- `--output-dir`: Save FIJI results to a different directory than JPEG files
  ```bash
  python main.py "/path/to/source" "/path/to/jpeg" --output-dir "/path/to/results"
  ```

### Examples

**Linux/Mac:**
```bash
python3 main.py "/home/user/data/raw_tif" "/home/user/data/results"
```

**Windows (PowerShell):**
```powershell
python .\main.py "C:\Users\username\data\raw_tif" "C:\Users\username\data\results"
```

**Run only FIJI evaluation on existing JPEG folders:**
```bash
python main.py "/path/to/existing/jpeg/root/folder" "/path/to/results" --fiji-only
```

*Note: The source directory must contain the `Picture_00s_JPG` and `Picture_10s_JPG` subfolders with JPEG files. Both folders must contain the same number of images.*

## Output Files

After the workflow completes, you'll find:

- **JPEG files**: Organized in subfolders
  - `Picture_00s_JPG/` - 00s time point images
  - `Picture_10s_JPG/` - 10s time point images

- **FIJI Results** (in output directory):
  - `Particle_Analysis_Results.csv` - Particle measurements table with columns:
    - `Slice` - Original slice label or JPEG filename for the time point image
    - `Count` - Number of particles detected in the slice
    - `Total Area` - Total area of all detected particles in pixels
    - `Average Size` - Average particle area in pixels for that slice
    - `%Area` - Percentage of the slice area occupied by detected particles
    - `Mean` - Average mean intensity of the detected particles
## Installation

### Prerequisites

- Python 3.10 or higher
    1. Go to https://www.python.org/downloads/
    2. Download the latest Python installer
    3. Important: Check the box "Add Python to PATH" during installation
    4. Install and restart PowerShell
### Prerequisites

- Python 3.10 or higher
    1. Go to https://www.python.org/downloads/
    2. Download the latest Python installer
    3. Important: Check the box "Add Python to PATH" during installation
    4. Install and restart PowerShell
- Java Runtime Environment (JRE) installed
- Git (optional, for cloning the repository)
- **32GB+ RAM recommended** for large image stacks (>1000 images)

### Setup (Linux/Mac)

1. Clone the repository:
```bash
git clone https://github.com/polfab96/proto_eval.git
cd proto_eval
```

2. Create virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# or
pip install pillow pyimagej scyjava
```

### Setup (Windows with PowerShell)

1. Create a directory for the scripts:
```powershell
mkdir C:\Users\username\proto_eval
cd C:\Users\username\proto_eval
```

2. Clone repository (requires git):
```powershell
git clone https://github.com/polfab96/proto_eval.git .
```

3. Create virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:
```powershell
pip install pillow pyimagej scyjava
```
#### Setup without Admin rights (Windows)

1. Find your Python installation path. Open PowerShell and run:
```powershell
Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\Python" -Recurse -Filter "python.exe" | Select-Object FullName
```

2. Copy the full path (e.g., `C:\Users\fp25v407\AppData\Local\Programs\Python\Python313\python.exe`)

3. Install Pillow using Python directly:
```powershell
& "C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\PythonXXX\python.exe" -m pip install pillow
```

4. **Create a batch file** `run.bat` in your `proto_eval` folder with this content:
```batch
@echo off
"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\PythonXXX\python.exe" main.py %1 %2
```
(Replace `YOUR_USERNAME` and `PythonXXX` with your actual username and Python version)

5. Run the script from PowerShell:
```powershell
cd C:\Users\YOUR_USERNAME\proto_eval
.\run.bat "Z:\path\to\source" "Z:\path\to\destination"
```

## Dependencies

- **pillow**: Image format conversion (TIF ↔ JPEG)
- **pyimagej**: Python interface to ImageJ/Fiji
- **scyjava**: Java bridge for calling ImageJ functions

These are automatically installed via `pip install` from `pyproject.toml`.

## File Format Requirements

### Input TIF Files

TIF files must follow the naming pattern:
```
TimeXXXXX_WellXXXX_PointXXXX_TimeXXXXX_SeqXXXX.tif
```

- **Position 4** (second "TimeXXXXX") determines output subfolder:
  - `Time00000` → `Picture_00s_JPG` (00 second time point)
  - `Time00001` → `Picture_10s_JPG` (10 second time point)

Supported formats: `.tif`, `.tiff`

### Image Data

- 16-bit grayscale images are automatically converted to 8-bit with contrast stretching
- 8-bit and palette mode images are converted to 8-bit grayscale

## Troubleshooting

### Missing JPEG subfolders

Ensure your TIF filenames match the expected pattern with the second "TimeXXXXX" part being either `Time00000` or `Time00001`.

### FIJI fails to initialize

Ensure Java is installed and accessible:
```bash
java -version  # Should display Java version
```

### No images found in folders

The script expects JPG files in the `Picture_00s_JPG` and `Picture_10s_JPG` subfolders. Check that:
- The folders exist and contain JPG files
- File names follow the expected pattern
- Files are not corrupted

### Out of memory during FIJI processing

If you get out-of-memory errors with large image stacks:
- The script automatically tries virtual stacks first (uses disk instead of RAM)
- Falls back to regular stacks if virtual stacks fail
- Increase Java heap size by editing `fiji_eval.py`:
  ```python
  scyjava.config.add_option('-Xmx30g')  # Increase from default 25g
  ```
- The Java heap size (set by scyjava) is different from FIJI's internal memory setting
- For very large datasets (>10,000 images), consider processing in smaller batches
- Ensure your system has sufficient RAM (32GB+ recommended for large stacks)

### Stack size mismatch between timepoints

If you get an error about different numbers of slices in the two stacks:
- Ensure both `Picture_00s_JPG` and `Picture_10s_JPG` folders contain the same number of images
- Check that all images in both folders are valid JPEG files
- Verify that the filename parsing correctly separates images into the two timepoint folders

## Technical Details

### Image Processing Pipeline

1. **Contrast Stretching**: 16-bit values are linearly mapped to 0-255 range
2. **Smoothing**: 3×3 Gaussian filter applied to noise reduction
3. **Subtraction**: Pixel-by-pixel subtraction of 10s from 00s
4. **Inversion**: Values are inverted (white becomes black, vice versa)
5. **Thresholding**: Automatic threshold calculation using Default method
6. **Masking**: Converts to binary image (black and white only)
7. **Particle Analysis**: ImageJ identifies and measures individual particles:
   - Counts particles above size threshold
   - Measures morphological properties (area, perimeter, circularity, etc.)
   - Generates summary statistics
   - Results exported to CSV for downstream analysis

### Memory Optimization

- Images are loaded as virtual stacks when possible to minimize RAM usage
- Intermediate images are closed after processing
- Results are saved separately from processing

## Version History

### v0.2.6
- Implemented manual per-slice particle analysis to generate summary statistics
- Fixed CSV output to match Fiji macro format (1920 rows, one per slice)
- Removed dependency on ImageJ Summary window (not available in headless mode)
- Added proper slice labeling using original file names

### v0.2.4
- Fixed ResultsTable CSV export using correct API (column index instead of column name)
- Increased default Java heap size to 25GB for large image stacks
- Added debugging output for image stack sizes
- Clarified --fiji-only usage requirements

### v0.2.3
- Added --fiji-only option to run FIJI evaluation without TIF conversion
- Fixed memory issues by using virtual stacks for large image sets
- Fixed BlackBackground option setting using Prefs class
- Improved error handling and fallback mechanisms

### v0.2.2
- Fixed image opening method to use FolderOpener directly (matching original macro)
- Added validation for JPG files in input folders
- Improved error handling and debugging output

### v0.2.1
- Added particle analysis step
- CSV export of results table for quantitative analysis
- Enhanced output reporting

### v0.2.0
- Added FIJI evaluation integration
- Complete automated workflow
- Multiple output format support

### v0.1.0
- Initial TIF to JPEG conversion

```



