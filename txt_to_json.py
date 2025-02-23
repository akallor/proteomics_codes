import json

def text_to_json(text_file, json_file):
    keywords_dict = {}

    with open(text_file, "r") as f:
        for line in f:
            key_value = line.strip().split(":")
            if len(key_value) == 2:
                key, value = key_value
                keywords_dict[key.strip()] = value.strip()
            else:
                print(f"Skipping invalid line: {line.strip()}")

    with open(json_file, "w") as f:
        json.dump(keywords_dict, f, indent=4)

    print(f"Converted {text_file} to {json_file}")

# Example usage
text_to_json("keywords.txt", "keywords.json")
