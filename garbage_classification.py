# -*- coding: utf-8 -*-
"""Garbage_Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mQa5WO_RkfedDuV8krvKKMe8jnsRbN0N
"""

# ✅ Import required libraries
import tensorflow as tf
import zipfile
import os
import matplotlib.pyplot as plt

from google.colab import files
uploaded = files.upload()

# ✅ Extracting the zip file
zip_path = "archive.zip"
extract_path = "/content/data"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("✅ Dataset unzipped to:", extract_path)

# ✅ Correct dataset path
dataset_path = "/content/data/Garbage classification"

# ✅ List class names (should show 6)
import os
print("Classes in dataset:", os.listdir(dataset_path))

# 🔍 List all subdirectories and help find the correct path
for root, dirs, files in os.walk("/content/data"):
    print(root)

from tensorflow.keras.preprocessing import image_dataset_from_directory

# ✅ Parameters
batch_size = 32
img_height = 224
img_width = 224
validation_split = 0.2
seed = 123

# ✅ Create training dataset
train_ds = image_dataset_from_directory(
    dataset_path,
    validation_split=validation_split,
    subset="training",
    seed=seed,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

# ✅ Create validation dataset
val_ds = image_dataset_from_directory(
    dataset_path,
    validation_split=validation_split,
    subset="validation",
    seed=seed,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

# ✅ Print class names
class_names = train_ds.class_names
print("📂 Classes:", class_names)

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetV2B2

# ✅ Data Augmentation
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# ✅ Load EfficientNetV2B2
base_model = EfficientNetV2B2(
    include_top=False,
    weights="imagenet",
    input_shape=(224, 224, 3)  # or (img_height, img_width, 3)
)
base_model.trainable = True  # Start with unfreezing

# ✅ Freeze bottom 70% of layers
fine_tune_at = int(len(base_model.layers) * 0.7)
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

# ✅ Build the model
model = models.Sequential([
    data_augmentation,
    layers.Rescaling(1./255),
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(6, activation='softmax')  # 6 classes
])

# ✅ Compile with a low learning rate for fine-tuning
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ✅ Summary
model.summary()

# Fine-tune the new model
fine_tune_epochs = 15  # or 20 if time allows

history_aug = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=fine_tune_epochs
)

# ✅ Train for more epochs (Phase 2 Fine-tuning)
more_epochs = 15  # You can adjust to 10–20 based on patience

history_fine_more = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=more_epochs
)

import matplotlib.pyplot as plt

# ✅ Fix: Define total_epochs
total_epochs = len(history.history['accuracy']) + len(history_fine.history['accuracy'])

# ✅ Combine metrics from both training phases
acc = history.history['accuracy'] + history_fine.history['accuracy']
val_acc = history.history['val_accuracy'] + history_fine.history['val_accuracy']

loss = history.history['loss'] + history_fine.history['loss']
val_loss = history.history['val_loss'] + history_fine.history['val_loss']

epochs_range = range(total_epochs)

# ✅ Plot graphs
plt.figure(figsize=(16, 6))

plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Train Accuracy')
plt.plot(epochs_range, val_acc, label='Val Accuracy')
plt.legend(loc='lower right')
plt.title('📈 Accuracy Over Epochs')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Train Loss')
plt.plot(epochs_range, val_loss, label='Val Loss')
plt.legend(loc='upper right')
plt.title('📉 Loss Over Epochs')

plt.show()

import numpy as np  # ✅ Add this at the top

# ⚠️ Only works if val_ds is not shuffled/batched
val_images = []
val_labels = []

for images, labels in val_ds.unbatch().take(1000):  # Use 1000 samples to speed things up
    val_images.append(images.numpy())
    val_labels.append(labels.numpy())

val_images = np.array(val_images)
val_labels = np.array(val_labels)

# ✅ Predict class probabilities
pred_probs = model.predict(val_images, verbose=1)
pred_labels = np.argmax(pred_probs, axis=1)

# ✅ Generate Classification Report
from sklearn.metrics import classification_report, confusion_matrix

print(classification_report(val_labels, pred_labels, target_names=class_names))

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# Generate confusion matrix
cm = confusion_matrix(val_labels, pred_labels)

# Plot it
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("🧾 Confusion Matrix")
plt.show()

from google.colab import files
uploaded = files.upload()

from tensorflow.keras.preprocessing import image
img_path = list(uploaded.keys())[0]
img = image.load_img(img_path, target_size=(img_height, img_width))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0) / 255.0

prediction = model.predict(img_array)
predicted_class = class_names[np.argmax(prediction[0])]
confidence = np.max(prediction[0]) * 100

print(f"📦 Predicted: {predicted_class} ({confidence:.2f}%)")