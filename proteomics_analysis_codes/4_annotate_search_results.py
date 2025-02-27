#!/usr/bin/env python


#Code to concatenate all data frames and annotate the peptides obtained from the database searching.


import os
import argparse
import pdb
import pickle as pkl
from os.path import exists
import numpy as np
import pandas as pd
from Bio import SeqIO
from tools import get_mapped_proteins, get_prot
from tqdm import tqdm

def process_files(samples_list, database_w_neoORFs, output_path, study_id):
    column_converter = {'ion.tsv': 'Peptide Sequence'}
    db = {}
    mappings = {}
    for record in SeqIO.parse(database_w_neoORFs, format='fasta'):
        header = record.id
        if not header.startswith('rev_'):
            if header.startswith('ENSP'):
                splits = header.split('|')
                for index, key in enumerate(['Protein', 'Transcript', 'gene', 'Gene Name']):
                    try:
                        mappings[key].append(splits[index])
                    except KeyError:
                        mappings[key] = [splits[index]]
            seq = str(record.seq)
            db[header] = seq
    df_mappings = pd.DataFrame(mappings)
    mapping_dict = df_mappings.set_index('Gene')['Gene Name'].to_dict()

    print('processing files')
    file_types = ['peptide.tsv', 'psm.tsv', 'ion.tsv']
    df = {}
    for file_type in file_types:
        print(f"processing {file_type}")
        df_list = []
        peptide_column = column_converter.get(file_type, 'Peptide')
        for sample in tqdm(samples_list):
            temp_df = pd.read_csv(os.path.join(sample, file_type), sep='\t', header=0, low_memory=False)
            temp_df.insert(0, 'Sample Name', os.path.basename(sample))
            temp_df.insert(0, 'Study ID', study_id)
            # lost information due to unusual header information
            temp_df.drop(['Protein', 'Protein ID', 'Entry Name', 'Gene', 'Protein Description', 'Mapped Genes', 'Mapped Proteins'],
                         axis=1, inplace=True)
            df_list.append(temp_df)
        df[file_type] = pd.concat(df_list)

    print('Getting mapped proteins information')
    peptides = []
    peptides.extend(list(df['peptide.tsv'].Peptide.unique()))
    peptides.extend(list(df['psm.tsv'].Peptide.unique()))
    peptides.extend(list(df['ion.tsv']['Peptide Sequence'].unique()))
    peptides = list(set(peptides))
    prot_dict = get_mapped_proteins(peptides, db)

    for file_type, df_type in df.items():
        peptide_column = column_converter.get(file_type, 'Peptide')
        sdf = pd.DataFrame({peptide_column: df_type[peptide_column].unique()})
        sdf['Mapped Proteins'] = sdf[peptide_column].map(prot_dict)
        # remove contaminants
        sdf = sdf[~sdf['Mapped Proteins'].map(lambda x: any([y.startswith('sp') for y in x.split(', ')]))]
        # add Transcript and Gene information
        sdf['Mapped Transcripts'] = sdf['Mapped Proteins'].str.extractall('(ENST[0-9]+)').reset_index().groupby('level_0').agg({0: lambda x: ', '.join(set(x))})
        sdf['Mapped Genes'] = sdf['Mapped Proteins'].str.extractall('(ENSG[0-9]+)').reset_index().groupby('level_0').agg({0: lambda x: ', '.join(set(x))})
        sdf['Mapped Genes'] = sdf['Mapped Genes'].fillna('')
        sdf['Mapped Gene Names'] = sdf['Mapped Genes'].map(lambda x: ', '.join(set([mapping_dict.get(y, '') for y in x.split(', ')])))
        sdf['Peptide Type'] = sdf['Mapped Proteins'].map(lambda x: all([y.startswith(("taa", "trans")) for y in x.split(', ')]))
        sdf['Peptide Type'] = sdf['Peptide Type'].map({True: 'trans peptide', False: 'regular peptide'})
        df_type = df_type.merge(sdf, how='right')
        df[file_type] = df_type

    df['peptide.tsv'].to_csv(os.path.join(output_path, 'peptide.tsv'), sep='\t', header=True, index=False)
    df['psm.tsv'].to_csv(os.path.join(output_path, 'psm.tsv'), sep='\t', header=True, index=False)
    df['ion.tsv'].to_csv(os.path.join(output_path, 'ion.tsv'), sep='\t', header=True, index=False)

def main():
    parser = argparse.ArgumentParser(description="Process files and generate output.")
    parser.add_argument("--samples_list", type=str, required=True, nargs='+', help="List of sample directories.")
    parser.add_argument("--database_w_neoORFs", type=str, required=True, help="Path to the database with neoORFs.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output files.")
    parser.add_argument("--study_id", type=str, required=True, help="Study ID to insert into the files.")

    args = parser.parse_args()
    process_files(args.samples_list, args.database_w_neoORFs, args.output_path, args.study_id)

if __name__ == "__main__":
    main()

