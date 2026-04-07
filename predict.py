import keras
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

classes = ['flip_left', 'flip_right', 'no_action']
def loadModel():
    model = keras.models.load_model("cnn2.keras")
    return model

def prediction(img,model,debug=False):
    #predictions = model.predict(img)
    logits = model.predict(img)
    predicted_index = np.argmax(logits,axis=1)[0]
    probs = tf.nn.softmax(logits[0]).numpy()
    confidence = probs[predicted_index]
    label = classes[predicted_index]
    
    if debug:
        print(f"Raw logits: {logits[0]}")
        print(f"Probabilities: {probs}")
    print(f"Prediction: {label} ({confidence:.2%})")
    return predicted_index, label, confidence
