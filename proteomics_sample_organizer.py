#Automatically organize all the raw data files into samples as soon as they are downloaded.


import os
import re
import shutil
from pathlib import Path
import argparse

def extract_sample_name(filename):
    """
    Extract sample name from filename using multiple strategies.

    Strategy priority:
    1. Look for pattern before '_Rep\d+'
    2. Look for pattern before '_\d+' (for files like 'Sample_01.raw')
    3. Look for pattern before last digit sequence
    """
    # Remove extension
    base_name = os.path.splitext(filename)[0]

    # Strategy 1: Look for '_Rep\d+' pattern
    match = re.search(r'^(.*?)_Rep\d+', base_name)
    if match:
        sample_name = match.group(1)
        # Remove date prefix if present
        date_match = re.search(r'^\d+_(.+)$', sample_name)
        if date_match:
            return date_match.group(1)
        return sample_name

    # Strategy 2: Look for '_\d+' pattern
    match = re.search(r'^(.*?)_\d+', base_name)
    if match:
        sample_name = match.group(1)
        # Remove date prefix if present
        date_match = re.search(r'^\d+_(.+)$', sample_name)
        if date_match:
            return date_match.group(1)
        return sample_name

    # Strategy 3: Look for the last digit sequence
    match = re.search(r'^(.*?)\d+[^A-Za-z]*$', base_name)
    if match and match.group(1):
        # Remove trailing non-alphanumeric chars
        sample_name = re.sub(r'[^A-Za-z0-9]+$', '', match.group(1))
        # Remove date prefix if present
        date_match = re.search(r'^\d+_(.+)$', sample_name)
        if date_match:
            return date_match.group(1)
        return sample_name

    # If no pattern found, check if there's a date prefix to remove
    date_match = re.search(r'^\d+_(.+)$', base_name)
    if date_match:
        return date_match.group(1)

    # Last resort: use the whole base name
    return base_name

def organize_samples(root_dir, dry_run=False):
    """Organize raw data files into sample folders."""
    # Get all directories starting with PXD or MSV
    dataset_dirs = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and (item.startswith('PXD') or item.startswith('MSV')):
            dataset_dirs.append(item_path)

    results = []
    for dataset_dir in dataset_dirs:
        dataset_name = os.path.basename(dataset_dir)
        print(f"Processing dataset: {dataset_name}")

        # Get all raw files in the dataset directory
        raw_files = []
        for file in os.listdir(dataset_dir):
            if file.upper().endswith('.RAW') or file.upper().endswith('.WIFF'):
                raw_files.append(file)

        # Group files by sample names
        samples = {}
        for file in raw_files:
            sample_name = extract_sample_name(file)
            if sample_name not in samples:
                samples[sample_name] = []
            samples[sample_name].append(file)

        # Create sample directories and move files
        for sample_name, files in samples.items():
            sample_dir_name = f"sample_{sample_name}"
            sample_dir_path = os.path.join(dataset_dir, sample_dir_name)

            if not os.path.exists(sample_dir_path) and not dry_run:
                os.makedirs(sample_dir_path)

            print(f"  Sample: {sample_name} - {len(files)} files")
            for file in files:
                src_path = os.path.join(dataset_dir, file)
                dst_path = os.path.join(sample_dir_path, file)

                if dry_run:
                    print(f"    Would move: {file} to {sample_dir_name}/")
                else:
                    print(f"    Moving: {file} to {sample_dir_name}/")
                    shutil.move(src_path, dst_path)

            result = {
                "dataset": dataset_name,
                "sample": sample_name,
                "files": files
            }
            results.append(result)

    return results

def main():
    parser = argparse.ArgumentParser(description="Organize proteomics raw data files into sample groups")
    parser.add_argument("root_dir", help="Root directory containing PXD and MSV datasets")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them")
    parser.add_argument("--verbose", action="store_true", help="Print detailed sample name extraction information")
    args = parser.parse_args()

    print(f"{'DRY RUN - ' if args.dry_run else ''}Organizing samples in {args.root_dir}")
    organize_samples(args.root_dir, args.dry_run)
    print("Done!")

if __name__ == "__main__":
    main()
