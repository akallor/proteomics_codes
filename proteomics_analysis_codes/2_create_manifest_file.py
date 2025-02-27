#!/usr/bin/env python

#!/usr/bin/env python

#Code to create a manifest file to run Fragpipe

import os
import argparse
from glob import glob
import numpy as np
import pandas as pd

def create_manifest(mzml_files, samples_file, output_file):
    new_files = glob(mzml_files)

    with open(samples_file, "r") as f:
        lines = f.read().splitlines()

    sample_name_dict = {}
    for file_name in new_files:
        for line in lines:
            if line.strip() in file_name:
                sample_name_dict[file_name] = "sample_" + line.strip()

    # Create a list of sample names corresponding to new_files
    sample_name = [sample_name_dict.get(file, 'default_value') for file in new_files]

    manifest = pd.DataFrame({'path': new_files, 'experiment name': sample_name})
    manifest['replicate name'] = np.nan
    manifest['type'] = 'DDA'
    manifest.to_csv(output_file, sep='\t', header=False, index=False)

def main():
    parser = argparse.ArgumentParser(description="Create a manifest file from sample data.")
    parser.add_argument("--mzml_files", type=str, required=True, help="Path to the mzML files (e.g., '/path/to/*.mzML').")
    parser.add_argument("--samples_file", type=str, required=True, help="Path to the samples.txt file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save the output manifest file.")

    args = parser.parse_args()
    create_manifest(args.mzml_files, args.samples_file, args.output_file)

if __name__ == "__main__":
    main()

