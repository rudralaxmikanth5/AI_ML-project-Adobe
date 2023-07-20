import os
import logging
import sys
import re

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

gl_chunk_size = 1500

def remove_br_tags(line):
    # Remove <br> tags from the line
    # line = re.sub(r'<br>', '', line)
    # line = re.sub(r'<br />', '', line)
    # line = re.sub(r'<br></br>', '', line)
    # line = re.sub(r'</br>', '', line)
    # line = re.sub(r'></a>', '', line)
    # line = re.sub(r'<a', '', line)
    return line

def split_context_file(input_dir, output_dir, chunk_size=gl_chunk_size):
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            input_file = os.path.join(root, file_name)

            rel_path = os.path.relpath(input_file, input_dir)

            output_subdir = os.path.dirname(rel_path)
            output_subdir_path = os.path.join(output_dir, output_subdir)
            os.makedirs(output_subdir_path, exist_ok=True)

            with open(input_file, "r", encoding="utf-8") as file:
                lines = file.readlines()
                heading = next((line for line in lines if line.startswith("#")), "").strip()

                split_parts = []
                current_part = ""
                current_word_count = 0

                for line in lines:

                    if current_word_count >= chunk_size and ( line.startswith("<a") or line.startswith("###") or line.startswith("##")):
                        if current_part:
                            split_parts.append(current_part.strip())
                            current_part = ""
                            current_word_count = 0
                    current_part += line
                    current_word_count += len(line.split())

                if current_part:
                    split_parts.append(current_part.strip())

                file_name_without_extension = os.path.splitext(file_name)[0]

                for i, part in enumerate(split_parts):
                    if i >= 1:
                        split_file_name = f"{file_name_without_extension}_{str(i)}.md"
                        output_file_path = os.path.join(output_subdir_path, split_file_name)
                        with open(output_file_path, "w", encoding="utf-8") as output_file:
                            output_file.write(remove_br_tags(heading)+ "\n"+" "+ remove_br_tags(part))
                    else:
                        split_file_name = f"{file_name_without_extension}.md"
                        output_file_path = os.path.join(output_subdir_path, split_file_name)
                        with open(output_file_path, "w", encoding="utf-8") as output_file:
                            output_file.write(remove_br_tags(part))

                    logging.debug(f"Processed: {input_file} -> {output_file_path}")

# Usage example:
input_dir = "raw_data"
output_dir = "chunk_data"
split_context_file(input_dir, output_dir)
