from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json
import pickle
import requests
import json
import re 

file_path = "token.txt"
with open(file_path, 'r', encoding='utf-8') as file:
    content34 = file.read()

ds_directory='data_processing/dataset'

with open(ds_directory + '/context_map.json', encoding='utf-8') as f:
    file_map = json.loads(f.read())


IMS_Org_ID = '90FC331D59DBA35E0A494204@AdobeOrg'
API_key = 'uxp-gentech-client'
access_token = content34
headers = {
    'x-gw-ims-org-id': IMS_Org_ID,
    'x-api-key': API_key,
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}


def remove_br_tags(line):
    # Remove <br> tags from the line
    line = re.sub(r'<br>', '', line)
    line = re.sub(r'<br />', '', line)
    line = re.sub(r'<br></br>', '', line)
    line = re.sub(r'</br>', '', line)
    line = re.sub(r'></a>', '', line)
    line = re.sub(r'<a', '', line)
    line = re.sub(r'</tr>', '', line)
    line = re.sub(r'<tr>', '', line)
    line = re.sub(r'</td>', '', line)
    line = re.sub(r'<th>', '', line)
    line = re.sub(r'</th>', '', line)
    line = re.sub(r'---', '', line)
    return line

class QuestionAnswering:
    def __init__(self):

        with open("Weights/tokenizer.json", "r", encoding='utf-8') as f:
            tokenizer_json = f.read()
            self.tokenizer = tokenizer_from_json(tokenizer_json)

        with open("Weights/label_encoder.pkl", "rb") as f:
            self.label_encoder = pickle.load(f)

        self.loaded_model = load_model("Weights/Classifier.h5")

    def process_question(self, question):
        processed_question = self.tokenizer.texts_to_sequences([question])
        processed_question = pad_sequences(processed_question, maxlen=50, padding='post')
        return processed_question

    def predict_labels(self, processed_question):
        predicted_labels_one_hot = self.loaded_model.predict(processed_question)
        predicted_labels = self.label_encoder.inverse_transform(np.argmax(predicted_labels_one_hot, axis=1))
        predicted_indices = np.argsort(predicted_labels_one_hot, axis=1)[:, -3:]
        return predicted_labels, predicted_indices

    def write_context_files(self, context_paths):
        for i, context_path in enumerate(context_paths):
            print(context_path)
            with open(f"predicted_Context/Context{i+1}.md", "w", encoding='utf-8') as f:
                with open("data_processing/"+context_path, "r", encoding='utf-8') as context_file:
                    content = context_file.read()
                    f.write(re.sub(r'[*#|]', '', remove_br_tags(content)))

    def generate_output_file(self, predicted_labels,question):
        print("Output file generated.")

        with open("Predicted_Context/Context1.md", "r", encoding='utf-8') as file:
            uxpdoc1 = file.read()
        with open("Predicted_Context/Context2.md", "r", encoding='utf-8') as file:
            uxpdoc2 = file.read()
            
        with open("Predicted_Context/Context3.md", "r", encoding='utf-8') as file:
            uxpdoc3 = file.read()

        uxpdoc = uxpdoc3 +"/n"+ uxpdoc2 +"/n"+ uxpdoc1

        return uxpdoc 

    def extract(self,response_data):
        # print(response_data)
        generations = response_data.get('generations', [])
        for generation in generations:
            for message in generation:
                if 'message' in message:
                    content = message['message'].get('content')
                    
        return content
        
    def save_response_data(self,response_data, filename):
        with open(filename, "w") as f:
            json.dump(response_data, f, indent=4)

    def run_question_answering(self,question):
        while True:
            if question.lower() == "quit":
                break

            processed_question = self.process_question(question)
            predicted_labels, predicted_indices = self.predict_labels(processed_question)

            context_paths = []
            for index in predicted_indices[0]:
                context_paths.append(file_map[str(self.label_encoder.classes_[index])]) 

            self.write_context_files(context_paths)
            Context=self.generate_output_file(predicted_labels,question)

            
            # prompt = f'''Generate an answer for the following question: '{question}'. 
            #            The answer should be strictly based on the context provided:'{Context}'. 
            #            And don't include comment and Your Respoonse should be only answer .
            #            Also don't include any other text. if any code part is preset in the response add ``` at begning and ending of code part.'''


            # prompt=f'''Generate answer from the given context. 
            #         \n------------\n
            #         context: {Context} 
            #         \n------------\n
            #         question: {question}
            #         \n------------\n
            #          Assume no prior knowledge and restrict answer from given context only. If you don't know the answer say,
            #         "I can't answer the question from the given documentation. If you think this is an error, please report by giving a feedback."

            # '''

            prompt=f'''Generate answer from the given context. context: {Context} question: {question} Assume no prior knowledge and restrict answer from given context only. If you don't know the answer say, "I can't answer the question from the given documentation. If you think this is an error, please report by giving a feedback."'''



            data = {
                'dialogue': {
                    'question': prompt
                },
                'llm_metadata': {
                    'model_name': 'gpt-35-turbo',
                    'temperature': 0.0,
                    'max_tokens': 350,
                    'top_p': 1.0,
                    'frequency_penalty': 0,
                    'presence_penalty': 0,
                    
                    'n': 1,
                    'llm_type': 'azure_chat_openai'
                }
            }
            response = requests.post("https://firefall-dev-va7.stage.cloud.adobe.io/v1/completions", headers=headers, data=json.dumps(data))
            try:
                response_data = response.json()
                print(response_data)
                Content1 = self.extract(response_data)

            except json.decoder.JSONDecodeError:
                print("Invalid JSON response received.")

            return Content1