# Proto Eval

A script to convert .tif files to JPEG format and organize them into subfolders based on filename patterns.

## Usage

Run the script with two arguments: the source directory containing .tif files and the destination directory.

```bash
python3 main.py "/path/to/source/directory" "/path/to/destination/directory"
```

For example:
```bash
python3 main.py "D:\.20260331 Proto motility assay Elanco\20260331_183427_027" "D:\.20260331 Proto motility assay Elanco\260331_proto_jpeg"
```
Or
```bash
uv run main.py "/mnt/d/.20260331_Proto_motility_assay_Elanco/20260403_Assay 2/20260402_141749_062" "/mnt/d/.20260331_Proto_motility_assay_Elanco/260403_proto_jpeg"
```

The script will:
- Scan the source directory for .tif and .tiff files
- Extract the subfolder name from the filename (second "TimeXXXXX" part)
- Create subfolders in the destination directory as needed
- Convert each .tif to JPEG and save in the appropriate subfolder

## Dependencies

- Python 3.13+
- Pillow (PIL) for image processing