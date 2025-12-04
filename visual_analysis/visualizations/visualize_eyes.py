import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.metrics import classification_report

data = np.load("visual_analysis/classifiers/eye_color.npz")
X = data["X"]
y = data["y"]

model = pickle.load(open("visual_analysis/embeddings/eye_color.pkl", "rb"))
label_encoder = pickle.load(open("visual_analysis/embeddings/eye_color_labels.pkl", "rb"))

# Encode and decode labels
y_true = label_encoder.transform(y)
y_pred = model.predict(X)

class_names = list(label_encoder.classes_)
num_classes = len(class_names)

# Generate Confusion Matrix
matrix = np.zeros((num_classes, num_classes), dtype=int)

for t, p in zip(y_true, y_pred):
    matrix[t][p] += 1

plt.figure(figsize=(6,6))
plt.imshow(matrix)
plt.title("Eye Color – Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.xticks(range(num_classes), class_names)
plt.yticks(range(num_classes), class_names)

for i in range(num_classes):
    for j in range(num_classes):
        plt.text(j, i, str(matrix[i][j]), ha="center", va="center")

plt.show()

# Accuracy
accuracy = np.mean(y_true == y_pred) * 100
print(f"\nAccuracy: {accuracy:.2f}%")

# Report
print("\nClassification Report:\n")
print(classification_report(y_true, y_pred, target_names=class_names))

