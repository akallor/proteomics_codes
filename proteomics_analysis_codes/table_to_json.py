import pandas as pd
import json
import os

def convert_to_json(input_file, output_file="keywords.json"):
    # Determine file type based on extension
    file_ext = os.path.splitext(input_file)[-1].lower()

    # Read the input file accordingly
    if file_ext == ".csv":
        df = pd.read_csv(input_file)
    elif file_ext == ".tsv":
        df = pd.read_csv(input_file, sep="\t")
    elif file_ext == ".xlsx":
        df = pd.read_excel(input_file)
    else:
        raise ValueError("Unsupported file format. Use CSV, TSV, or XLSX.")

    # Convert to dictionary (key-value pairs)
    keywords_dict = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

    # Save as JSON
    with open(output_file, "w") as f:
        json.dump(keywords_dict, f, indent=4)

    print(f"Converted {input_file} to {output_file}")

# Example usage:
convert_to_json("keywords.xlsx")  # Replace with "keywords.csv" or "keywords.tsv" as needed
