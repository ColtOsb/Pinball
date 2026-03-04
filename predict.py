import keras
import matplotlib.pyplot as plt

def loadModel():
    model = keras.models.load_model("trained.keras")
    return model

def prediction(img,model):
#    img_array = keras.utils.img_to_array(img)
#    img_array = keras.ops.expand_dims(img_array, 0)  # Create batch axis

    predictions = model.predict(img)
    score = float(keras.ops.sigmoid(predictions[0][0]))
    print(predictions)
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


