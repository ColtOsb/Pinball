import keras
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

classes = ['flip_left', 'flip_right', 'no_action']
def loadModel():
    model = keras.models.load_model("cnn2.keras")
    return model

def prediction(img,model):
    predictions = model.predict(img)
    probs = tf.nn.softmax(predictions[0]).numpy()
    predicted_index = np.argmax(probs)
    confidence = probs[predicted_index]
    label = classes[predicted_index]
    
    print(f"Raw logits: {predictions[0]}")
    print(f"Probabilities: {probs}")
    print(f"Prediction: {label} ({confidence:.2%})")
    return predicted_index, label, confidence
