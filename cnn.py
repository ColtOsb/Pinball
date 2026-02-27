import numpy as np
import keras
import keras.layers as layers
from sklearn.model_selection import train_test_split
from zipfile import ZipFile
import cv2
import glob
import os



image_root = '/home/pi/vision/dataset/'

def getImagePaths(root,folder_names,extensions):
    values = []
    for folder_name, extension in zip(folder_names,extensions):
        values.append(glob.glob(os.path.join(root,folder_name,extension)))
    return tuple(values)

states = {"name":"lung","root":image_root,"classes":['no_action','flip_left','flip_right']}
no_action_images, flip_left_images, flip_right_images = getImagePaths(image_root,("no_action","flip_left","flip_right"),("*.jpg", "*.jpg","*.jpg"))
states["images"] = {"no_action":no_action_images,"flip_left":flip_left_images,"flip_right":flip_right_images}

print("-----STATES-----")
print(f"no_action_images: {len(no_action_images)}")
print(f"flip_left_images: {len(flip_left_images)}")
print(f"flip_right_images: {len(flip_right_images)}")

img_size = (290,135)
split = 0.2
epochs = 10
batch_size = 64


def load_images(image_paths,img_size):
    if not isinstance(img_size,tuple):
        img_size = (img_size,img_size)
    images = []
    for path in image_paths:
        img = cv2.imread(path)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = cv2.resize(img,(img_size[0],img_size[1]))
        images.append(img)
    return np.array(images,dtype='float32')/255.0


image_paths = []
labels = []
count = 0
for x in states["classes"]:
    image_paths += states["images"][x]
    print(x)
    labels += [count] * len(states["images"][x])
    count = count + 1

X_train_paths, X_temp_paths, y_train, y_temp = train_test_split(
        image_paths,
        labels,
        test_size = split*2,
        random_state = 42,
        stratify = labels
    )
    
X_val_paths, X_test_paths, y_val, y_test = train_test_split(
    X_temp_paths,
    y_temp,
    test_size = 0.5,
    random_state = 42,
    stratify = y_temp
)


print(f"\nData split:")
print(f"Training samples: {len(X_train_paths)} ({len(X_train_paths)/len(image_paths)*100:.1f}%)")
print(f"Validation samples: {len(X_val_paths)} ({len(X_val_paths)/len(image_paths)*100:.1f}%)")
print(f"Test samples: {len(X_test_paths)} ({len(X_test_paths)/len(image_paths)*100:.1f}%)")

print(f"\nTraining set distribution: {np.bincount(y_train)}")
print(f"Validation set distribution: {np.bincount(y_val)}")
print(f"Test set distribution: {np.bincount(y_test)}")



states["X_train"] = load_images(X_train_paths,img_size)
states["X_val"] = load_images(X_val_paths,img_size)
states["X_test"] = load_images(X_test_paths,img_size)

states["y_train"] = np.array(y_train)
states["y_val"] = np.array(y_val)
states["y_test"] = np.array(y_test)

print(f"X_train shape: {states['X_train'].shape}")
print(f"X_val shape: {states['X_val'].shape}")
print(f"X_test shape: {states['X_test'].shape}")



from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

states["model"] = keras.models.Sequential()

#First Layer
states["model"].add(Conv2D(32,(3,3),activation='relu',input_shape=(img_size[0],img_size[1],3)))
states["model"].add(MaxPooling2D((2,2)))
#Second Layer
states["model"].add(Conv2D(64,(3,3),activation='relu'))
states["model"].add(MaxPooling2D((2,2)))
#Third Layer
states["model"].add(Conv2D(128,(3,3),activation='relu'))
states["model"].add(MaxPooling2D((2,2)))
#Convert and Output
states["model"].add(Flatten())
states["model"].add(Dense(128,activation='relu'))
states["model"].add(Dense(3,activation='softmax'))

states["model"].compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
states["model"].summary()

states["history"] = states["model"].fit(
        states["X_train"],
        states["y_train"],
        batch_size=16,
        epochs=1,
        validation_data=(states["X_val"],states["y_val"])
    )
    
print('Evaluate on Test Data')
test_loss,test_accuracy = states["model"].evaluate(states["X_test"],states["y_test"],batch_size=128)
print('Test Loss: ',test_loss)
print('Test Accuracy: ',test_accuracy)

import matplotlib.pyplot as plt
print(f"-----{states['name']}-----")
# summarize history for accuracy
plt.plot(states["history"].history['accuracy'])
plt.plot(states["history"].history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(states["history"].history['loss'])
plt.plot(states["history"].history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

states["model"].save("trained.keras")
