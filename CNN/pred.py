# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 11:22:11 2023

@author: T14 Gen 3
"""
""" GPU不好可以換成CPU跑，解開這段即可
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
"""

from tensorflow.keras import layers ,Model
from tensorflow import keras
from keras.models import load_model
import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Dropout ,Dense
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt
import os ,shutil ,pathlib
from tensorflow.keras.utils import image_dataset_from_directory
from sklearn.metrics import confusion_matrix

width=320
height=240
#load訓練好的模型路徑
test_model = keras.models.load_model("chi102_VGG_42_0.314917.keras")

#預測圖片路徑
test_data_path=pathlib.Path("picture/test")

test_dataset=image_dataset_from_directory(
  test_data_path,
  image_size=(width,height),
  batch_size=32
  )

#評估模型
test_loss, test_acc = test_model.evaluate(test_dataset)
print(f"test acc:{test_acc:.3f}")

#預測模型
true_labels = []
predicted_labels = []
for images, labels in test_dataset:
    true_labels.extend(labels.numpy())
    predictions = test_model.predict(images)
    predicted_labels.extend(np.argmax(predictions, axis=1))

print("True labels:", true_labels)
print("Predicted labels:", predicted_labels)

conf_matrix = confusion_matrix(true_labels ,  predicted_labels)
print("Confusion Matrix:",conf_matrix)