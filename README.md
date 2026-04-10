# Proto Eval

A script to convert .tif files to JPEG format and organize them into subfolders based on filename patterns.

## Usage

Run the script with two arguments: the source directory containing .tif files and the destination directory.

```bash
python3 main.py "/path/to/source/directory" "/path/to/destination/directory"
```

For example (Windows):
```bash
python .\main.py "Z:\Gruppen\IPA\starving Echino\7 - Echino multi IPA Projects\2026_Proto drug testing Elanco - Heinz Sager\20260403_Assay_2\20260402_141749_062" "Z:\Gruppen\IPA\starving Echino\7 - Echino multi IPA Projects\2026_Proto drug testing Elanco - Heinz Sager\260403_proto_jpeg"
```


The script will:
- Scan the source directory for .tif and .tiff files
- Extract the subfolder name from the filename (second "TimeXXXXX" part)
- Create subfolders in the destination directory as needed
- Convert each .tif to JPEG and save in the appropriate subfolder

## Dependencies

- Python 3.13+
- Pillow (PIL) for image processing

## Setup (Windows)
1. Open powershell either via search bar or Windows + R

2. Create a directory (folder) to store the scripts
```bash
mkdir  C:\Users\username\name-of-directory
cd  C:\Users\username\name-of-directory
```

3. Download scripts (needs git installed)
```bash
git clone https://github.com/polfab96/proto_eval.git name_of_directory
```

4. Download dependencies
Python: https://www.python.org/downloads/
IMPORTANT: Check the box "Add Python to PATH"
Restart PowerShell

```Bash
pip install pillow
```

5. Double check the paths and run the script.


