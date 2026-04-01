import keras
import numpy as np
import matplotlib.pyplot as plt

classes = ['no_action', 'flip_left', 'flip_right']
def loadModel():
    model = keras.models.load_model("cnn2.keras")
    return model

def prediction(img,model):
#    img_array = keras.utils.img_to_array(img)
#    img_array = keras.ops.expand_dims(img_array, 0)  # Create batch axis

    predictions = model.predict(img)
    #score = float(keras.ops.sigmoid(predictions[0][0]))
    print("Raw predictions:", predictions)

    predicted_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_index]

    print(f"PREDICT: {classes[predicted_index]}({confidence:.2%})")
    return predicted_index
    """
    #NO ACTION
    if predictions[0][0]:
        print("PREDICT: NO_ACTION")
        return 1
    #FLIP LEFT
    if predictions[0][1]:
        print("PREDICT: FLIP_LEFT")
        return 2
    #FLIP RIGHT
    if predictions[0][2]:
        print("PREDICT: FLIP_RIGHT")
        return 3
    return 0

    """

if __name__ == "__main__":
    model = loadModel()
    test_image = "/dataset/no_action/image0.jpg"
    
    img = test_image
    prediction = prediction(img,model)
    score = float(keras.ops.sigmoid(prediction[0][0]))
    print(f"This image is {100 * (1 - score):.2f}% cat and {100 * score:.2f}% dog.")
