# -*- coding: utf-8 -*-


"""CPU跑才解開
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
"""


from tensorflow.keras import layers ,Model,regularizers,optimizers
from tensorflow import keras
import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Dropout ,Dense
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt
import  pathlib
from tensorflow.keras.utils import image_dataset_from_directory 


width=320
height=240
category=7 

train_data_path=pathlib.Path("picture/train") 
test_data_path=pathlib.Path("picture/test")
validation_data_path=pathlib.Path("picture/validation")


train_dataset=image_dataset_from_directory(
 train_data_path,
 image_size=(width,height), 
 batch_size=32
 )

test_dataset=image_dataset_from_directory(
 test_data_path,
 image_size=(width,height), 
 batch_size=32)

validation_dataset=image_dataset_from_directory(
 validation_data_path,
 image_size=(width,height), 
 batch_size=32
 )



data_augmentation=keras.Sequential(
    [
     layers.RandomFlip("horizontal"),
     layers.RandomRotation(45),
     layers.RandomZoom(0.3)
     ]
    )

inputs=keras.Input(shape=(width,height,3)) 
x=data_augmentation(inputs)
x=layers.Rescaling(1./255)(x)
x=layers.Conv2D(32, 3,activation="relu",padding="same")(x)
x=layers.Conv2D(32, 3,activation="relu",padding="same")(x)
x=layers.MaxPooling2D(pool_size=2)(x)
x=layers.Conv2D(64, 3,activation="relu",padding="same")(x)
x=layers.Conv2D(64, 3,activation="relu",padding="same")(x)
x=layers.MaxPooling2D(pool_size=2)(x)
x=layers.Conv2D(128, 3,activation="relu",padding="same")(x)
x=layers.Conv2D(128, 3,activation="relu",padding="same")(x)
x=layers.MaxPooling2D(pool_size=2)(x)
x=layers.Conv2D(256, 3,activation="relu",padding="same")(x)
x=layers.Conv2D(256, 3,activation="relu",padding="same")(x)
x=layers.GlobalAveragePooling2D()(x)


x=layers.Dense(128)(x)
x=layers.Dropout(0.5)(x)
outputs=layers.Dense(category,activation="softmax")(x) 
model=keras.Model(inputs,outputs)
#optimizer=optimizers.Adam(learning_rate=0.00001)
optimizer=optimizers.RMSprop(learning_rate=0.0001)
#optimizers.RMSprop()
model.compile(optimizer=optimizer,loss="sparse_categorical_crossentropy",metrics=["acc"])


callbacks=[
    # keras.callbacks.EarlyStopping(
    #     monitor="val_acc",
    #     patience=2,
    #     verbose=1
    #     ),
    keras.callbacks.ModelCheckpoint(
        filepath='chi102_VGG_{epoch:02d}_{val_loss:4f}.keras',
        save_best_only=True,
        monitor="val_loss",
        verbose=1
        )
    ]


history=model.fit(
    train_dataset,
    epochs=50,
    validation_data=validation_dataset,
    callbacks=callbacks
    )


acc=history.history["acc"]
val_acc=history.history["val_acc"]
loss=history.history["loss"]
val_loss=history.history["val_loss"]
epochs=range(1,len(acc)+1)
plt.plot(epochs,acc,"bo",label="Training acc")
plt.plot(epochs,val_acc,"b",label="validation acc")
plt.title("Training and Validation acc")
plt.legend()
plt.figure()
plt.plot(epochs,loss,"bo",label="Training loss")
plt.plot(epochs,val_loss,"b",label="validation loss")
plt.title("Training and Validation loss")
plt.legend()
plt.show()