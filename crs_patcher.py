"""
LINKS: The Challenge of Golf CRS Course Patcher

This script patches course files in CRS format used by LINKS: The Challenge of Golf to allow for 
compatibility with the Memorex VIS version of the game.

It removes specified files from the archive and rebuilds the file index with correct offsets.

Usage:
    python crs_patcher.py <file.CRS>                    # Process single file
    python crs_patcher.py <file1.CRS> <file2.CRS> ...   # Process multiple files  
    python crs_patcher.py <directory>                   # Process all CRS files in directory

Output Structure:
    Creates 'patched/' directory with 'logs/' subdirectory

Requirements:
    - Python 3.6+
    - No external dependencies (uses only standard library)
"""

import sys
import os
import datetime
from datetime import UTC
from typing import List, Tuple, Optional
from pathlib import Path

# CRS archive file block signature - 'MDmd' in ASCII
MDMD_SIGNATURE = b'MDmd'
OFFSET_AFTER_PATTERN = 0x2A
NAME_LEN = 17
HEADER_SIZE = 122  # CRS archive header size in bytes
TIME_OFFSET = datetime.timedelta(hours=4, minutes=30)

# Configurable list of files to remove from CRS archive - users can easily add more
FILES_TO_REMOVE = [
    b'PATCH.OFS',
    b'OBJECT.OFS',
    # Add more file signatures here as needed:
]

def get_file_modification_time(filepath: str) -> datetime.datetime:
    """Get file modification time in UTC using cross-platform methods."""
    mod_time_seconds = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(mod_time_seconds, UTC)

def find_all_mdmd_patterns(data: bytearray) -> List[int]:
    """Find all MDmd pattern positions using optimized scanning."""
    positions: List[int] = []
    pos = 0
    while pos < len(data):
        index = data.find(MDMD_SIGNATURE, pos)
        if index == -1:
            break
        positions.append(index)
        pos = index + 1
    return positions

def remove_files_from_archive(data: bytearray, pattern_positions: List[int], files_to_remove: Optional[List[bytes]] = None) -> bytearray:
    """
    Remove specified files from CRS archive using reverse-order deletion.
    
    Identifies file blocks by signatures and removes them entirely while
    maintaining correct indices during the removal process.
    """
    if files_to_remove is None:
        files_to_remove = FILES_TO_REMOVE
    
    if not files_to_remove or not pattern_positions:
        return data
    
    files_to_delete: List[Tuple[int, int, str]] = []
    
    for i, pattern_pos in enumerate(pattern_positions):
        file_start = pattern_pos
        file_end = pattern_positions[i + 1] if i + 1 < len(pattern_positions) else len(data)
        
        file_data = data[file_start:file_end]
        for signature in files_to_remove:
            if signature in file_data:
                filename = signature.decode('ascii', errors='ignore')
                print(f"Removing file: {filename} (0x{file_start:06X}-0x{file_end:06X})")
                files_to_delete.append((file_start, file_end, filename))
                break
    
    if not files_to_delete:
        print("No files found matching the specified signatures")
        return data
    
    # Remove in reverse order to maintain indices
    files_to_delete.sort(key=lambda x: x[0], reverse=True)
    cleaned_data = data[:]
    
    for file_start, file_end, filename in files_to_delete:
        del cleaned_data[file_start:file_end]
    
    print(f"Removed {len(files_to_delete)} files from archive")
    return cleaned_data

def process_archive(filepath: str) -> Tuple[List[bytearray], bytearray, int, List[int]]:
    """Process CRS archive: remove unwanted files and generate index blocks."""
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())

    # Remove unwanted files
    all_positions = find_all_mdmd_patterns(data)
    data = remove_files_from_archive(data, all_positions)

    # Build final index after file removal
    positions = find_all_mdmd_patterns(data)
    index_blocks: List[bytearray] = []
    final_positions: List[int] = []
    filenames_to_exclude = {sig.decode('ascii', errors='ignore').upper() for sig in FILES_TO_REMOVE}

    for pos in positions:
        name_start = pos + OFFSET_AFTER_PATTERN
        name_end = name_start + 32
        name_bytes = data[name_start:name_end].split(b'\x20', 1)[0][:13]
        
        filename_ascii = name_bytes.decode('ascii', errors='ignore').upper()
        if filename_ascii in filenames_to_exclude:
            continue
        
        index_block = bytearray(NAME_LEN)
        index_block[:len(name_bytes)] = name_bytes
        index_blocks.append(index_block)
        final_positions.append(pos)

    # Calculate and update offsets
    file_count = len(index_blocks)
    base_offset = (file_count * NAME_LEN) + HEADER_SIZE

    print(f"Processing {file_count} files")
    print(f"Base offset: 0x{base_offset:X}")

    for index_block, pos in zip(index_blocks, final_positions):
        final_offset = pos + base_offset
        index_block[13:16] = final_offset.to_bytes(3, byteorder='little')

    return index_blocks, data, file_count, final_positions

def build_header_dynamically(file_count: int, filepath: str) -> Tuple[bytearray, int, int]:
    """
    Build CRS archive header dynamically.
    
    Creates a 122-byte header following the CRS format specification.
    See README.md for detailed format documentation.
    """
    header = bytearray(HEADER_SIZE)
    
    # Archive signature and format metadata
    header[0x00:0x04] = MDMD_SIGNATURE
    header[0x04] = 0x0A  # ReleaseLevel (v1.0)
    header[0x05] = 0x01  # HeaderType
    header[0x06:0x08] = HEADER_SIZE.to_bytes(2, byteorder='little')
    
    # File count and index table sizes
    header[0x0A:0x0C] = file_count.to_bytes(2, byteorder='little')
    table_size_bytes = (file_count * NAME_LEN).to_bytes(2, byteorder='little')
    header[0x19:0x1B] = table_size_bytes
    header[0x1D:0x1F] = table_size_bytes
    
    # File timestamps (MS-DOS format)
    mod_date = get_file_modification_time(filepath) + TIME_OFFSET
    dos_year = mod_date.year - 1980
    dos_date = (dos_year << 9) | (mod_date.month << 5) | mod_date.day
    dos_time = (mod_date.hour << 11) | (mod_date.minute << 5) | (mod_date.second // 2)
    header[0x23:0x25] = dos_time.to_bytes(2, byteorder='little')
    header[0x25:0x27] = dos_date.to_bytes(2, byteorder='little')
    
    # Index identifier with length prefix
    header[0x29] = 0x07
    header[0x2A:0x31] = b'~INDEX~'
    
    # Padding pattern
    for i in range(0x31, 0x36):
        header[i] = 0x20
    header[0x36] = 0x00
    for i in range(0x37, 0x7A):
        header[i] = 0x20
    
    return header, dos_time, dos_date

def replace_internal_paths(data: bytearray, target_path: str = "C:\\LINKS\\TEMP\\") -> bytearray:
    """Replace internal file paths in CRS archive with target path."""
    MDMD_FILE_HEADER_PATTERN = bytes.fromhex("4D 44 6D 64 0A 01 7A 00 00 00 00 00")
    PATH_OFFSET_IN_HEADER = 0x36
    
    path_bytes = target_path.encode('ascii')
    path_segment = bytes([len(path_bytes)]) + path_bytes
    
    total_replacements = 0
    search_pos = 0

    while True:
        pattern_pos = data.find(MDMD_FILE_HEADER_PATTERN, search_pos)
        if pattern_pos == -1:
            break

        path_start = pattern_pos + PATH_OFFSET_IN_HEADER
        path_end = path_start + len(path_segment)
        
        if path_end >= len(data):
            print(f"Warning: Skipping path replacement at offset 0x{pattern_pos:06X} - would exceed buffer")
            search_pos = pattern_pos + 1
            continue
        
        data[path_start:path_end] = path_segment
        total_replacements += 1

        # Pad remaining space with spaces
        pos = path_end
        while pos < len(data) and data[pos] != 0x20:
            data[pos] = 0x20
            pos += 1

        search_pos = pattern_pos + 1

    print(f"Path replacements: {total_replacements}")
    return data

def assemble_and_save(header: bytearray, index_blocks: List[bytearray], data: bytearray, original_filename: str, output_dir: Optional[str] = None) -> str:
    """Assemble and save the patched CRS file with optional output directory."""
    index_table = b''.join(index_blocks)
    new_content = bytearray(header + index_table + data)
    new_content = replace_internal_paths(new_content)

    new_filename = _get_output_path(original_filename, "_patched", output_dir)
    
    with open(new_filename, 'wb') as f:
        f.write(new_content)

    # Preserve timestamps
    stat = os.stat(original_filename)
    os.utime(new_filename, (stat.st_atime, stat.st_mtime))

    print(f"Modified file saved as: {os.path.abspath(new_filename)}")
    return str(new_filename)

def generate_log(index_blocks: List[bytearray], positions: List[int], base_offset: int, original_filename: str, file_count: int, dos_time: int, dos_date: int, log_dir: Optional[str] = None) -> None:
    """Generate processing log with optional log directory."""
    log_lines: List[str] = [
        "Generated index summary",
        "------------------------",
        f"Number of files: {file_count}",
        f"Index size: {file_count * NAME_LEN} bytes (0x{file_count * NAME_LEN:04X})"
    ]

    hour = (dos_time >> 11, (dos_time >> 5) & 0b111111, (dos_time & 0b11111) * 2)
    date = ((dos_date >> 9) + 1980, (dos_date >> 5) & 0b1111, dos_date & 0b11111)

    log_lines.extend([
        f"MS-DOS Time: {hour[0]:02}:{hour[1]:02}:{hour[2]:02} (HEX: {dos_time.to_bytes(2, 'little').hex(' ').upper()})",
        f"MS-DOS Date: {date[0]}-{date[1]:02}-{date[2]:02} (HEX: {dos_date.to_bytes(2, 'little').hex(' ').upper()})",
        ""
    ])

    for i, (index_block, original_offset) in enumerate(zip(index_blocks, positions)):
        adjusted = original_offset + base_offset
        hex_block = index_block.hex().upper()
        try:
            ascii_name = index_block.split(b'\x00')[0].decode('ascii')
        except UnicodeDecodeError:
            ascii_name = "NON-PRINTABLE NAME"

        log_lines.append(f"[{i}] Original offset: 0x{original_offset:06X} → "
                        f"Adjusted offset: 0x{adjusted:06X} → "
                        f"Name HEX: {hex_block} → "
                        f"ASCII: {ascii_name}")

    log_name = _get_output_path(original_filename, "_patched_log.txt", log_dir)
    
    with open(log_name, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

    print(f"Validation log generated as: {os.path.abspath(log_name)}")

def _get_output_path(original_filename: str, suffix: str, output_dir: Optional[str] = None) -> Path:
    """Helper function to generate output file paths consistently."""
    original_path = Path(original_filename)
    name = original_path.stem
    ext = original_path.suffix if suffix.endswith('_log.txt') else original_path.suffix
    filename = f"{name}{suffix}{ext}" if not suffix.endswith('.txt') else f"{name}{suffix}"
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / filename
    return original_path.parent / filename

def find_crs_files(path: str) -> List[str]:
    """Find all CRS files in the given path (file or directory)."""
    path_obj = Path(path)
    
    if path_obj.is_file():
        if path_obj.suffix.upper() == '.CRS':
            return [str(path_obj)]
        else:
            print(f"Warning: {path} is not a CRS file")
            return []
    elif path_obj.is_dir():
        crs_files: List[Path] = []
        for pattern in ['*.crs', '*.CRS']:
            crs_files.extend(list(path_obj.glob(pattern)))
        return [str(f) for f in sorted(crs_files)]
    else:
        print(f"Error: {path} is not a valid file or directory")
        return []

def process_single_file(filepath: str, output_dir: Optional[str] = None, log_dir: Optional[str] = None) -> bool:
    """Process a single CRS file, returning True if successful."""
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(filepath)}")
        print(f"{'='*60}")
        
        index_blocks, filtered_data, file_count, positions = process_archive(filepath)
        header, dos_time, dos_date = build_header_dynamically(file_count, filepath)
        assemble_and_save(header, index_blocks, filtered_data, filepath, output_dir)
        base_offset = (file_count * NAME_LEN) + HEADER_SIZE
        generate_log(index_blocks, positions, base_offset, filepath, file_count, dos_time, dos_date, log_dir)
        
        print(f"✓ Successfully processed {os.path.basename(filepath)}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(filepath)}: {str(e)}")
        return False

def process_batch(file_paths: List[str], create_directories: bool = True) -> Tuple[int, int]:
    """Process multiple CRS files with organized output structure."""
    if not file_paths:
        print("No CRS files found to process")
        return 0, 0
    
    successful = 0
    total = len(file_paths)
    output_dir = log_dir = None
    
    if create_directories and total >= 1:
        first_file_dir = Path(file_paths[0]).parent
        output_dir = str(first_file_dir / "patched")
        log_dir = str(Path(output_dir) / "logs")
        
        print(f"Batch processing {total} CRS file{'s' if total > 1 else ''}")
        print(f"Output directory: {os.path.abspath(output_dir)}")
        print(f"Log directory: {os.path.abspath(log_dir)}")
    
    for filepath in file_paths:
        if process_single_file(filepath, output_dir, log_dir):
            successful += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Files processed: {successful}/{total}")
    if successful < total:
        print(f"Failures: {total - successful}")
    
    return successful, total

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("LINKS: The Challenge of Golf CRS Course Patcher")
        print("=" * 50)
        print("Patches CRS course files for Memorex VIS compatibility")
        print()
        print("Usage:")
        print("  python crs_patcher.py <file.CRS>                    # Process single file")
        print("  python crs_patcher.py <file1.CRS> <file2.CRS> ...   # Process multiple files")
        print("  python crs_patcher.py <directory>                   # Process all CRS files in directory")
        print()
        print("Output Structure:")
        print("  All processing: Creates 'patched/' directory with 'logs/' subdirectory")
        print()
    else:
        # Collect all file paths from arguments
        all_files: List[str] = []
        for arg in sys.argv[1:]:
            all_files.extend(find_crs_files(arg))
        
        if not all_files:
            print("No CRS files found to process")
            sys.exit(1)
        
        # Remove duplicates while preserving order
        unique_files = list(dict.fromkeys(all_files))
        
        # Always use batch processing with organized directories
        process_batch(unique_files)
