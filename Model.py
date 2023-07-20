import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

class Classifier:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.label_encoder = LabelEncoder()
        self.model = None

    def load_data(self):
        with open('pklfiles/train.pkl', 'rb') as f:
            train_data = pickle.load(f)

        with open('pklfiles/test.pkl', 'rb') as f:
            validation_data = pickle.load(f)

        train_questions = [item['question'] for item in train_data]
        train_ids = [item['id'] for item in train_data]

        validation_questions = [item['question'] for item in validation_data]
        validation_ids = [item['id'] for item in validation_data]

        self.tokenizer.fit_on_texts(train_questions)

        vocab_size = len(self.tokenizer.word_index) + 1

        # Calculate the maximum length from the training questions
        global max_length
        # max_length = max(len(sequence.split()) for sequence in train_questions) 
        max_length =50
        embedding_dim = 64

        train_sequences = self.tokenizer.texts_to_sequences(train_questions)
        train_padded = pad_sequences(train_sequences, maxlen=max_length, padding='post')

        validation_sequences = self.tokenizer.texts_to_sequences(validation_questions)
        validation_padded = pad_sequences(validation_sequences, maxlen=max_length, padding='post')

        self.label_encoder.fit(train_ids)
        num_classes = len(self.label_encoder.classes_)
        train_labels = self.label_encoder.transform(train_ids)
        validation_labels = self.label_encoder.transform(validation_ids)
        train_labels_one_hot = to_categorical(train_labels, num_classes=num_classes)
        validation_labels_one_hot = to_categorical(validation_labels, num_classes=num_classes)

        return train_padded, train_labels_one_hot, validation_padded, validation_labels_one_hot, vocab_size, embedding_dim, num_classes

    def build_model(self, vocab_size, embedding_dim, max_length, num_classes):
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
            tf.keras.layers.Conv1D(filters=64, kernel_size=(3), strides=(1), padding='same', activation='relu'),
            tf.keras.layers.GlobalMaxPooling1D(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            # tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def train_model(self):
        train_padded, train_labels_one_hot, validation_padded, validation_labels_one_hot, vocab_size, embedding_dim, num_classes = self.load_data()
        self.model = self.build_model(vocab_size, embedding_dim, max_length, num_classes=num_classes)
        # Train the model and get the training history
        callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)
        self.model.fit(train_padded, train_labels_one_hot, epochs=20, batch_size=32,callbacks=[callback],validation_data=(validation_padded, validation_labels_one_hot))

        # # Access the training history
        # training_loss = history.history['loss']
        # training_accuracy = history.history['accuracy']
        # validation_loss = history.history['val_loss']
        # validation_accuracy = history.history['val_accuracy']

        # # Plot the training and validation metrics
        # plt.figure(figsize=(12, 4))
        # plt.subplot(1, 2, 1)
        # plt.plot(training_loss, label='Training Loss')
        # plt.plot(validation_loss, label='Validation Loss')
        # plt.xlabel('Epochs')
        # plt.ylabel('Loss')
        # plt.legend()

        # plt.subplot(1, 2, 2)
        # plt.plot(training_accuracy, label='Training Accuracy')
        # plt.plot(validation_accuracy, label='Validation Accuracy')
        # plt.xlabel('Epochs')
        # plt.ylabel('Accuracy')
        # plt.legend()

        # plt.tight_layout()
        # plt.show()

    def save_model(self):
        self.model.save("weights/Classifier.h5")
        self.model.save_weights("weights/Classifier_weights.h5")

    def save_tokenizer(self):
        with open("weights/tokenizer.json", "w") as f:
            f.write(self.tokenizer.to_json())

    def save_label_encoder(self):
        with open("weights/label_encoder.pkl", "wb") as f:
            pickle.dump(self.label_encoder, f)

classifier = Classifier()
classifier.train_model()
classifier.save_model()
classifier.save_tokenizer()
classifier.save_label_encoder()
