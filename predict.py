import keras
import cv2
import numpy as np
import matplotlib.pyplot as plt

classes = ['no_action', 'flip_left', 'flip_right']
def loadModel():
    model = keras.models.load_model("cnn2.keras")
    return model

def prediction(img,model):
    """
    predictions = model.predict(img)
    print("Raw predictions:", predictions)

#    predicted_index = np.argmax(predictions)
#    confidence = predictions[0][predicted_index]

    print(f"PREDICT: {classes[predicted_index]}({confidence:.2%})")
    return predicted_index

if __name__ == "__main__":
    model = loadModel()
    test_image = "/dataset/no_action/image0.jpg"
    
    img = test_image
    prediction = prediction(img,model)
    score = float(keras.ops.sigmoid(prediction[0][0]))
    """
    #img = cv2.imread(img,cv2.IMREAD_GRAYSCALE)
    #img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    #img = cv2.resize(img,(290,235))
    #img = img.astype('float32') / 255.0
    #img = np.expand_dims(img,axis=0)

    predictions = model.predict(img)
    predicted_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_index]
    label = classes[predicted_index]

    print(f"Prediction: {label} ({confidence:.2%})")
    return predicted_index, label, confidence
