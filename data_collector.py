import os
import re
import shutil
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Copy all relevant .md files from the input folder to the output folder
def copy_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Recursively traverse the input folder
    for root, dirs, files in os.walk(input_folder):
        if ".github" in dirs:
            dirs.remove(".github")
        counter = 1
        for file in files:
            if file.endswith(".md") and file not in [ 'CODE_OF_CONDUCT.md', '.gitignore', 'README.md']:
                input_file = os.path.join(root, file)
                output_file = os.path.join(output_folder, os.path.relpath(input_file, input_folder))

                # Check if the file contains the string pattern "Do not import"
                with open(input_file, "r") as file_obj:
                    content = file_obj.read()
                    if not re.search(r'import\s+Content\s+from\s', content):
                        # Create the output file's directory if it doesn't exist
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)

                        # Copy the .md file to the output folder
                        shutil.copyfile(input_file, output_file)
                        logging.debug(f"Copied: {input_file} -> {output_file}")
                    else:
                        logging.debug(f"Skipped: {input_file}")

        