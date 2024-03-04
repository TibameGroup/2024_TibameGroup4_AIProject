# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 08:27:02 2023

@author: T14 Gen 3
"""
""" GPU不好可以換成CPU跑，解開這段即可
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
"""
from tensorflow.keras import layers ,Model
from tensorflow import keras
import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Dropout ,Dense
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt
import  pathlib
from tensorflow.keras.utils import image_dataset_from_directory 



width=640
height=480
category=3 

train_data_path=pathlib.Path("train")
test_data_path=pathlib.Path("test")
validation_data_path=pathlib.Path("validation")
train_dataset=image_dataset_from_directory(
 train_data_path,
 image_size=(width,height), #圖片大小
 batch_size=32
 )
test_dataset=image_dataset_from_directory(
  test_data_path,
  image_size=(width,height), #圖片大小
  batch_size=32
  )
validation_dataset=image_dataset_from_directory(
 validation_data_path,
 image_size=(width,height), #圖片大小
 batch_size=32
 )

#VGG 模型特徵萃取(嫁接預訓練的深度學習模型)

conv_base=keras.applications.vgg16.VGG16(
    weights="imagenet",
    include_top=False  #不包含全連階層分類器 
    )
conv_base.trainable=False #訓練期間不更新權重


#資料增強 
data_augmentation=keras.Sequential(
    [
     layers.RandomFlip("horizontal"),
     layers.RandomRotation(45),
     layers.RandomZoom(0.3)
     ]
    )

inputs=keras.Input(shape=(width,height,3)) #照片大小
x=data_augmentation(inputs)
x=keras.applications.vgg16.preprocess_input(x)
x=conv_base(x)
x=layers.Flatten()(x)
x=layers.Dense(256)(x)
x=layers.Dropout(0.5)(x)
outputs=layers.Dense(category,activation="softmax")(x) #隨目標數修改
model=keras.Model(inputs,outputs)
model.compile(optimizer="rmsprop",loss="sparse_categorical_crossentropy",metrics=["acc"])
callbacks=[
    keras.callbacks.ModelCheckpoint(
        filepath='chi102_VGG_{epoch:02d}_{val_loss:4f}.keras',
        save_best_only=True,
        monitor="val_loss"
        )
    ]
history=model.fit(
    train_dataset,
    epochs=50,
    validation_data=validation_dataset,
    callbacks=callbacks
    )

#繪圖
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
plt.plot(epochs,acc,"bo",label="Training loss")
plt.plot(epochs,val_acc,"b",label="validation loss")
plt.title("Training and Validation loss")
plt.legend()
plt.show()