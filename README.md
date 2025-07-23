# Links: The Challenge of Golf - CRS File Patcher

A Python tool for patching CRS (compressed resource) files from Links: The Challenge of Golf to make them compatible with the Memorex VIS system.

## Overview

Links: The Challenge of Golf courses are stored in CRS format - essentially collections of compressed files using LZCD compression (based on MDCD, hence the "MDmd" signature). The Memorex VIS system only had one official course (TORREY_P.CRS), while additional courses were released for Microsoft Windows versions.

This script patches any CRS file to create the appropriate header and `~INDEX~` structure required for Memorex VIS compatibility by:

- Removing incompatible files (`PATCH.OFS`, `OBJECT.OFS`)
- Rebuilding the file index with correct offsets
- Updating internal file paths to `C:\LINKS\TEMP\`
- Preserving original file timestamps

## Features

- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Configurable file removal system** - easily add more files to exclude
- **Preserves file timestamps** across all operating systems
- **Efficient reverse-order deletion** algorithm maintains array indices
- **Detailed logging and validation** with hex dumps and offset tracking
- **Dynamic header generation** - no hardcoded binary blobs
- **Bounds checking** prevents buffer overflows
- **Batch processing support** - process multiple files or entire directories
- **Organized output structure** - automatic directory creation for batch operations

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Usage

### Single File Processing
```bash
python crs_patcher.py <course_file.CRS>
```

### Multiple File Processing
```bash
python crs_patcher.py <file1.CRS> <file2.CRS> <file3.CRS>
```

### Directory Processing
```bash
python crs_patcher.py <directory_path>
```

**Examples:**
```bash
# Process single file
python crs_patcher.py PEBBLE_BEACH.CRS

# Process multiple files
python crs_patcher.py TORREY_P.CRS PEBBLE_BEACH.CRS ST_ANDREWS.CRS

# Process all CRS files in a directory
python crs_patcher.py course_files/
```

### Output Structure

**Single File:**
- `COURSE_NAME_patched.CRS` - The patched course file
- `COURSE_NAME_patched_log.txt` - Detailed processing log

**Multiple Files/Directory:**
- `patched/` - Directory containing all patched CRS files
- `patched/logs/` - Directory containing all processing logs

## CRS File Format

### Header Structure (122 bytes total)

The CRS file format has been reverse-engineered with the following structure:

```
Offset    Size  Description
--------  ----  -----------
0x00-0x03   4   Archive signature 'MDmd' (identifies CRS format)
0x04        1   ReleaseLevel = 0x0A (10 = v1.0) - Archive format version
0x05        1   HeaderType = 0x01 (1) - Type of header structure  
0x06-0x07   2   HeaderSize = 0x7A (122) - Total header size (little-endian)
0x08-0x09   2   Reserved/padding
0x0A-0x0B   2   File count (little-endian)
0x0C-0x18  13   Reserved/padding
0x19-0x1A   2   Index table size (little-endian)
0x1B-0x1C   2   Reserved
0x1D-0x1E   2   Index table size duplicate (little-endian)
0x1F-0x22   4   Reserved
0x23-0x24   2   MS-DOS time (little-endian)
0x25-0x26   2   MS-DOS date (little-endian)
0x27-0x28   2   Reserved
0x29        1   Length prefix for identifier = 0x07
0x2A-0x30   7   "~INDEX~" identifier (length-prefixed string)
0x31-0x35   5   Padding with spaces
0x36        1   Null byte separator = 0x00
0x37-0x79  67   Padding with spaces
```

### Index Structure

Following the 122-byte header is the file index table:

- **Entry Size:** 17 bytes per file
- **Format:** 13 bytes filename + 3 bytes offset + 1 byte padding
- **Filename:** ASCII, space-padded, null-terminated
- **Offset:** 24-bit little-endian offset to compressed file data
- **Total Size:** `file_count × 17` bytes

### Compressed File Format (122 bytes total)

Each file in the archive uses the MDmd compression format with the following header structure:

```
Offset    Size  Description
--------  ----  -----------
0x00-0x03   4   Signature 'MDmd' (identifies compressed file format)
0x04        1   ReleaseLevel = 0x0A (10 = v1.0) - Compression version
0x05        1   HeaderType = 0x01 (1) - Header type (only type 1 currently)
0x06-0x07   2   HeaderSize = 0x7A (122) - Size of this header (little-endian)
0x08-0x17  16   Reserved/padding (UserInfo, Reserved1, Reserved2, Reserved3)
0x18        1   CompressType = 0x01 (1) - Type of compression used (1 = LZCD)
0x19-0x1C   4   OrigFileSize - Original file size in bytes (little-endian)
0x1D-0x20   4   CompFileSize - Compressed file size in bytes (little-endian)
0x21-0x22   2   FileAttr - Original file attributes (little-endian)
0x23-0x24   2   FileTime - Original file time (little-endian)
0x25-0x26   2   FileDate - Original file date (little-endian)
0x27-0x28   2   FileCRC - File CRC checksum (little-endian)
0x29        1   FileName length prefix (String12 format)
0x2A-0x35  12   FileName data (exactly 12 bytes, space-padded if shorter)
0x36        1   PathName length prefix (DirStr format)
0x37-0x44  14   PathName data ("C:\LINKS\TEMP\" - 14 bytes)
0x45-0x79  53   Padding with spaces (0x20) to reach exactly 122 bytes
0x7A+       ?   Compressed file data follows
```

**Key Details:**
- **Total header size:** Fixed at 122 bytes (0x7A), padded with spaces (0x20) to exact size
- **String format:** Pascal-style with length prefix byte followed by string data
- **Padding:** FileName field is always 12 bytes, space-padded if filename is shorter
- **Path padding:** After PathName data, header is padded with spaces to reach 122 bytes
- **Endianness:** All multi-byte integers are little-endian
- **Path replacement:** This tool modifies the PathName field at offset 0x36+ to `C:\LINKS\TEMP\`

## Technical Details

### File Processing Flow

1. **Load Archive:** Read entire CRS file into memory
2. **Pattern Detection:** Scan for all MDmd signatures using optimized string search
3. **File Removal:** Identify and remove unwanted files using reverse-order deletion
4. **Index Generation:** Build new file index with updated offsets
5. **Header Creation:** Generate 122-byte archive header with timestamps
6. **Path Replacement:** Update internal file paths in compressed blocks
7. **Assembly:** Combine header + index + data and save with preserved timestamps

### Algorithm Complexity

- **Pattern Search:** O(n×m) where n=file size, m=pattern length (4 bytes)
- **File Removal:** O(k) where k=number of files to remove
- **Index Building:** O(f) where f=number of files in archive
- **Overall:** Linear O(n) performance for typical archive sizes

### Memory Usage

The tool loads the entire archive into memory for processing. For typical Links course files (1-2MB), this provides optimal performance. For very large archives, a streaming approach could be implemented.

## Configuration

### Adding Files to Remove

Edit the `FILES_TO_REMOVE` list in the script:

```python
FILES_TO_REMOVE = [
    b'PATCH.OFS',
    b'OBJECT.OFS',
    # Add more file signatures here as needed:
]
```

### Customizing Paths

The default replacement path is `C:\LINKS\TEMP\`. To use a different path:

```python
# In replace_internal_paths function call
new_content = replace_internal_paths(new_content, "D:\\GAMES\\LINKS\\")
```

## Troubleshooting

### Common Issues

**"No files found matching the specified signatures"**
- The CRS file may not contain PATCH.OFS/OBJECT.OFS files
- This is normal for some course files

**"Warning: Skipping path replacement"**
- Indicates a corrupted or non-standard CRS file
- Check that the input file is a valid Links course archive

**File size differences**
- Minor size differences are normal due to removed files
- Use the generated log file to verify processing details

### Validation

Compare your patched file with known working VIS-compatible courses:
- File structure should match original VIS releases
- Index table should be properly aligned
- All file offsets should be valid

## Development

### Code Structure

- **Single-file design:** Easy deployment and maintenance
- **Type hints:** Full type annotation for better IDE support
- **Cross-platform:** Uses only standard library functions
- **Efficient algorithms:** Optimized for typical archive sizes
- **Error handling:** Bounds checking and graceful failure modes

### Testing

Test with various Links course files:
- Original VIS courses (TORREY_P.CRS)
- Windows expansion packs
- Third-party course files

## License

This project is released under the MIT License. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgments

- Links: The Challenge of Golf by Access Software
- Memorex VIS platform documentation
- LZCD/MDCD compression format research community

## Historical Context

The Memorex VIS (Video Information System) was a unique multimedia platform from the early 1990s that used CD-i technology. Links: The Challenge of Golf was one of its flagship titles, but the platform's limited success meant few additional courses were developed. This tool bridges that gap by making the extensive library of Windows-based Links courses compatible with the VIS system.
