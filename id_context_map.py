import os
import shutil
import re
import json

yaml_pattern = r'^---\n(.*\n)+?---\n'  # Pattern to match YAML front matter
regex = re.compile(yaml_pattern, re.MULTILINE | re.DOTALL)

ignore_pattern = r'\* \[.+?\]\(.+?\)'
regex_ignore = re.compile(ignore_pattern)

class FileExtractor:
    def __init__(self, source_dir, destination_dir):
        self.source_dir = source_dir
        self.destination_dir = destination_dir

    def extract_files(self):
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)

        counter = 1  # Initialize counter
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith('.md') and file != 'index.md':
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)
                elif file == 'index.md':
                    new_file_name = f'index-{counter}.md'  # Add counter to the file name
                    counter += 1  # Increment counter for the next file
                    new_file_path = os.path.join(self.destination_dir, new_file_name)
                    with open(os.path.join(root, file), 'r') as source_file:
                        lines = source_file.readlines()
                        filtered_lines = [line for line in lines if not regex_ignore.match(line.strip()) and line.strip() != '']
                        if len(filtered_lines) > 10:
                            with open(new_file_path, 'w') as destination_file:
                                destination_file.writelines(filtered_lines)
                            shutil.copy2(os.path.join(root, file), new_file_path)

    def process_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            pattern = r'import\s+Content\s+from\s'    # Ignoring this pattern
            if not re.search(pattern, content):
                shutil.copy2(file_path, self.destination_dir)

    def print_file_map(self):
        for source_file, destination_file in self.file_map.items():
            print(f'{source_file} => {destination_file}')


# Define the main directory
context_directory = "dataset"
main_directory = context_directory + "/docs"

source_dir = 'chunk_data/uxp-main'
destination_dir = main_directory + '/uxp-docs'

file_extractor = FileExtractor(source_dir, destination_dir)
file_extractor.extract_files()

source_dir = 'chunk_data/uxp-photoshop-main'
destination_dir = main_directory + '/ps-docs'

file_extractor = FileExtractor(source_dir, destination_dir)
file_extractor.extract_files()


# Define a counter for assigning IDs
ctxt_id = 0
ctxt_map = {}

# Iterate over the files in the main directory
for root, dirs, files in os.walk(main_directory):
    for file in files:
        file_name = file
        file_path = os.path.join(root, file)
        ctxt_map[ctxt_id] = file_path
        ctxt_id += 1
        continue


# Dump context map into a JSON file
with open(context_directory + "/context_map.json", 'w') as json_file:
    json.dump(ctxt_map, json_file)
