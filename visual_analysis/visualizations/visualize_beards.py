# visualize_beards_improved.py
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.metrics import classification_report
import seaborn as sns

data = np.load("visual_analysis/embeddings/beard.npz")
X = data["X"]
y = data["y"]

model = pickle.load(open("visual_analysis/classifiers/beard.pkl", "rb"))
label_encoder = pickle.load(open("visual_analysis/classifiers/beard_labels.pkl", "rb"))

y_true = label_encoder.transform(y)
y_pred = model.predict(X)

class_names = list(label_encoder.classes_)
print("Classes:", class_names)

# Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='viridis',
            xticklabels=class_names, yticklabels=class_names,
            cbar=False, linewidths=0.5, linecolor='gray')
plt.title("Facial Hair Confusion Matrix", fontsize=16, pad=20)
plt.xlabel("Predicted", fontsize=12)
plt.ylabel("True", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("beard_confusion_matrix.png", dpi=200)
plt.show()

# Accuracy
accuracy = np.mean(y_true == y_pred) * 100
print(f"\nStandard Accuracy: {accuracy:.2f}%")

allowed_pairs = {
    ("stubble", "none"), ("none", "stubble"),
    ("goatee", "full"), ("full", "goatee"),
}

tolerable_correct = 0
total = len(y_true)

for true_label, pred_label in zip(y, label_encoder.inverse_transform(y_pred)):
    true_str = true_label
    pred_str = pred_label

    if true_str == pred_str:
        tolerable_correct += 1
    elif (true_str, pred_str) in allowed_pairs:
        tolerable_correct += 1

revised_accuracy = (tolerable_correct / total) * 100
print(f"Revised Accuracy (allowing stubble<->none and goatee<->full): {revised_accuracy:.2f}%")
print("\nClassification Report:\n")
print(classification_report(y_true, y_pred, target_names=class_names))
