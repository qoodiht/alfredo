import json
import string
import random
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense, Dropout

nltk.download("punkt")
nltk.download("wordnet")
nltk.download('omw-1.4')

# load data
f = open("intents.json").read()
data = json.loads(f)

# set up data
words = []
classes = []
data_x = []  # patterns
data_y = []  # responses

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        tokens = nltk.word_tokenize(pattern)  # tokenize pattern
        words.extend(tokens)  # add tokens to words
        data_x.append(pattern)  # add each pattern to data_x
        data_y.append(intent["tag"])  # add each tag to data_y

    if intent["tag"] not in classes:  # learn new tags
        classes.append(intent["tag"])

# initialize lemmatizer for stem words
lemmatizer = WordNetLemmatizer()

# lemmatize all words and lower
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in string.punctuation]

# sort the vocabulary and classes alphabetically
words = sorted(set(words))
classes = sorted(set(classes))

# convert text to numbers
training = []
out_empty = [0] * len(classes)

# bag of words
for idx, doc in enumerate(data_x):
    bow = []
    text = lemmatizer.lemmatize(doc.lower())
    for word in words:
        bow.append(1) if word in text else bow.append(0)

    output_row = list(out_empty)
    output_row[classes.index(data_y[idx])] = 1
    # add this to training array
    training.append([bow, output_row])

# shuffle training data and convert to array
random.shuffle(training)
training = np.array(training, dtype=object)
# split in the different datas
train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

# set up model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation="softmax"))
adam = tf.keras.optimizers.Adam(learning_rate=0.01, decay=1e-6)
model.compile(loss="categorical_crossentropy",
              optimizer=adam,
              metrics=["accuracy"])
print(model.summary())
epoch = input("Enter training epochs: ")
model.fit(x=train_x, y=train_y, epochs=int(epoch), verbose=1)


# process input

def clean_text(text):
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens


def bag_of_words(text, vocab):
    tokens = clean_text(text)
    bow = [0] * len(vocab)
    for w in tokens:
        for idx, word in enumerate(vocab):
            if word == w:
                bow[idx] = 1
    return np.array(bow)


def pred_class(text, vocab, labels):
    bow = bag_of_words(text, vocab)
    resoult = model.predict(np.array([bow]))[0]  # get possibilities
    thresh = 0.5
    y_pred = [[indx, res] for indx, res in enumerate(resoult) if res > thresh]
    y_pred.sort(key=lambda x: x[1], reverse=True)  # order by probability
    return_list = []
    for r in y_pred:
        return_list.append(labels[r[0]])  # add high bossibility labbels
    # print("Prediction: " + str(return_list))
    return return_list


def get_response(intents_list, intents_json):
    if len(intents_list) == 0:
        resoult = "Lo siento, no te he entendido"
    else:
        tag = intents_list[0]  # highest possibility tag chossen
        list_of_intents = intents_json["intents"]
        for i in list_of_intents:
            if i["tag"] == tag:
                resoult = random.choice(i["responses"])
                break
    return resoult


#while True:
    #usr_inp = input("Tú: ")
    #if usr_inp == "exit":
    #    break
    #intents = pred_class(usr_inp, words, classes)
    #response = get_response(intents, data)
    #print("Alfredo: " + str(response))
