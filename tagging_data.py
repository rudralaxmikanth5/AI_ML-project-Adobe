import os
import json
import logging
import sys
import random
import pickle

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def llm_questions_tagging(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data_elements = []

    # Recursively iterate through all files and subdirectories in the input folder
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)

                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    data_elements.append(json_data)

    # Sort the data elements based on the 'id' field in increasing order
    data_elements.sort(key=lambda x: x.get('id', 0))

    # Create the final data structure
    data = {'Data Elements': data_elements}

    # Write the data to the output file
    output_file_path = os.path.join(output_folder, 'tagged_questions.json')
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Example usage:
input_folder = "data_processing/dataset/qstns"
output_folder = "ds_out"
# llm_questions_tagging(input_folder, output_folder)


import json
import random
import pickle

train_questions = []
test_questions = []

train_test_split = 0.8
#remove validation 
with open('ds_out/tagged_questions.json', 'r') as f:
    data = json.load(f)

    for element in data["Data Elements"]:
        file_id = element['id']
        questions = element['data']['questions']
        num_questions = len(questions)
        train_size = int(train_test_split * num_questions)
        train_questions.extend([{"id": file_id, "question": q} for q in questions[:train_size]])
        test_questions.extend([{"id": file_id, "question": q} for q in questions[train_size:]])

# random.shuffle(train_questions)
# random.shuffle(test_questions)
print("Total number of questions:", len(train_questions))
print("Total number of questions:", len(test_questions))

global train_set
train_set = train_questions
global test_set
test_set = test_questions

with open('pklfiles/train.pkl', 'wb') as f:
    pickle.dump(train_set, f)

with open('pklfiles/test.pkl', 'wb') as f:
    pickle.dump(test_set, f)
