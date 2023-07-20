# TODO: To be fixed
import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor
import time


ds_directory = "dataset"
ctxt_directory = ds_directory + "/docs"

ctxt_map = {}
with open(ds_directory + '/context_map.json') as f:
    ctxt_map = json.loads(f.read())

file_path = "token.txt"
with open(file_path, 'r') as file:
    content34 = file.read()

IMS_Org_ID = '90FC331D59DBA35E0A494204@AdobeOrg'
API_key = 'uxp-gentech-client'
access_token = content34
headers = {
    'x-gw-ims-org-id': IMS_Org_ID,
    'x-api-key': API_key,
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

def extract_qa_pairs(response_data):
    temp = []
    qa_pairs = []
    generations = response_data.get('generations', [])
    for generation in generations:
        for message in generation:
            if 'message' in message:
                content = '\n' + message['message'].get('content')
                if content:
                    pairs = content.split('\n\n')
                    for pair in pairs:
                        question = pair.split('\nQuestion')
                        temp = question[1:]
                        for text in temp:
                            if len(text.split(':')) > 1:
                                question_text = text.split(':')[1]
                            else:
                                question_text = text.split(':')[0]
                            qa_pair = question_text.strip()
                            qa_pairs.append(qa_pair)
    return qa_pairs[:-1]

def generate_qa(context, num):
    prompt = f""" Generate {num} unique questions.
                        Imagine yourself as a data analyst preparing a dataset that showcases various use cases.
                        Formulate the questions in a way that a developer would ask to determine which API to use for a specific task.
                        Most of the questions should follow the format "How can I accomplish a certain task?".
                        They should appear as if the person asking the question is seeking information without prior knowledge.
                        The questions should be based strictly on the provided contextual information:
                        Context: {context}
                        Differentiate each question using 'Question:' as a prefix.
                        """

    data = {
        'dialogue': {
            'question': prompt
        },
        'llm_metadata': {
            'model_name': 'gpt-35-turbo',
            'temperature': 0.0,
            'max_tokens': 2000,
            'top_p': 1.0,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'n': 1,
            'llm_type': 'azure_chat_openai'
        }
    }

    response = requests.post("https://firefall-dev-va7.stage.cloud.adobe.io/v1/completions", headers=headers,
                             data=json.dumps(data))
    try:
        response_data = response.json()
        qa_pairs = extract_qa_pairs(response_data)
        return {
            #'context_path': file_map[filename],
            'questions': qa_pairs
        }

    except json.decoder.JSONDecodeError:
        print("Invalid JSON response received.")
        return generate_qa(context, num)  # filename)
        

def process_file(file_path, counter):
    with open(file_path, 'r') as md_file:
        data = str(md_file.read())
        filename = os.path.basename(file_path)
        qa = generate_qa(data, num_per_context)  # , filename)
        data_dict = {
            'id': counter,
            'data': qa
        }
        file_name_without_ext = os.path.splitext(filename)[0]
        dataset_file_path = os.path.join(dataset_folder, f'{file_name_without_ext}.json')
        with open(dataset_file_path, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        time.sleep(15)


def run_thread_pools(file_paths,counter, batch_size, stop_after_batches=None):
 # Counter for assigning IDs
    total_batches = len(file_paths) // batch_size
    if len(file_paths) % batch_size != 0:
        total_batches += 1

    if stop_after_batches is not None:
        total_batches = min(total_batches, stop_after_batches)

    for batch_number in range(total_batches):
        start_index = batch_number * batch_size
        end_index = start_index + batch_size
        batch_file_paths = file_paths[start_index:end_index]

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            for file_path in batch_file_paths:
                executor.submit(process_file, file_path, counter)
                counter += 1

        if stop_after_batches is not None and batch_number + 1 == stop_after_batches:
            break

counter = 0 

# Generate questions for the first set of files
folder_path = ctxt_directory  + '/uxp-docs'
dataset_folder = ds_directory + '/qstns' + '/uxp-qstns'
os.makedirs(dataset_folder, exist_ok=True)
num_per_context = 80
file_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith('.md')]

batch_size = 16  # Set the desired batch size
stop_after_batches = None  # Set the number of batches to stop after (None to run until all batches are processed)
run_thread_pools(file_paths, counter ,batch_size, stop_after_batches)

print(f'Successfully generated files in the dataset folder: {dataset_folder}.')


# Generate questions for the second set of files
folder_path = ctxt_directory + '/ps-docs'
dataset_folder = ds_directory+ '/qstns' + '/ps-qstns'
os.makedirs(dataset_folder, exist_ok=True)
num_per_context = 80
file_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith('.md')]

# Get the last assigned ID from the previous folder
previous_folder_path = ctxt_directory + '/uxp-docs'
previous_dataset_folder = ds_directory + '/qstns' + '/uxp-qstns'
previous_files = [filename for filename in os.listdir(previous_dataset_folder) if filename.endswith('.json')]
if previous_files:
    valid_ids = []
    for filename in previous_files:
        file_path = os.path.join(previous_dataset_folder, filename)
        with open(file_path) as json_file:
            data = json.load(json_file)
            if 'id' in data and isinstance(data['id'], int):
                valid_ids.append(data['id'])
    last_assigned_id = max(valid_ids) if valid_ids else 0
else:
    last_assigned_id = 0
# Set the starting counter for the current folder
counter = last_assigned_id + 1
# print(counter)
batch_size = 16  # Set the desired batch size
stop_after_batches = None  # Don't stop after any specific number of batches (run until all batches are processed)
run_thread_pools(file_paths,counter, batch_size, stop_after_batches)

print(f'Successfully generated files in the dataset folder: {dataset_folder}.')
