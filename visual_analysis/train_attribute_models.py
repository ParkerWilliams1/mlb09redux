import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

def train_model(npz_file, model_out, labels_out):
    data = np.load(npz_file)
    X, y = data["X"], data["y"]

    print(f"Training model: {npz_file} — {len(X)} samples")

    enc = LabelEncoder()
    y_enc = enc.fit_transform(y)

    clf = LogisticRegression(max_iter=500)
    clf.fit(X, y_enc)

    pickle.dump(clf, open(model_out, "wb"))
    pickle.dump(enc, open(labels_out, "wb"))

    print(f"Saved model → {model_out}")
    print(f"Saved labels → {labels_out}\n")


if __name__ == "__main__":
    # train_model("eye_color.npz", "eye_color.pkl", "eye_color_labels.pkl")
    train_model("beard.npz", "beard.pkl", "beard_labels.pkl")