#!/usr/bin/env python

#Code to generate the proteomic search database


import os
import argparse
import pandas as pd

def prepare_database(input_db, input_neoORFs, output_db):
    df = pd.read_csv(input_neoORFs, sep='\t', header=0)
    df['header'] = df['key']
    df['peptide'] = df['peptide.normal.ends'].str.replace('*', '', regex=False)
    df = df[['header', 'peptide']].drop_duplicates()
    neoORF_lines = ('>' + df['header'] + '\n' + df['peptide'] + '\n').tolist()
    neoORF_rev_lines = ('>rev_' + df['header'] + '\n' + df['peptide'].map(lambda x: x[::-1]) + '\n').tolist()

    lines = []
    with open(input_db) as fh:
        for line in fh:
            lines.append(line)

    lines.extend(''.join(neoORF_lines))
    lines.extend(''.join(neoORF_rev_lines))

    with open(output_db, 'w') as fh:
        fh.write(''.join(lines))

def main():
    parser = argparse.ArgumentParser(description="Prepares fragpipe workflow by adding the database path and variable modifications.")
    parser.add_argument("--input_db", type=str, required=True, help="Path to the input database file.")
    parser.add_argument("--input_neoORFs", type=str, required=True, help="Path to the input neoORFs file.")
    parser.add_argument("--output_db", type=str, required=True, help="Path to save the output database file.")

    args = parser.parse_args()
    prepare_database(args.input_db, args.input_neoORFs, args.output_db)

if __name__ == "__main__":
    main()

