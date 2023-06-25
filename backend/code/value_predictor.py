import pickle

from backend.code.cache import Cache


class ValuePredictor:
    def __init__(self, download_model=True):
        if download_model:
            from huggingface_hub import hf_hub_download

            REPO_ID = "grasper/market-segmentation"
            FILENAME = "value_predictor_model.pkl"

            path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
            print("Using value_predictor_model downloaded from HuggingFace Hub.")
            with open(path, "rb") as file:
                model, label_embedding, scalar = pickle.load(file)
        else:
            print("Trying to use locally generated value_predictor_model.")
            model, label_embedding, scalar = Cache("value_predictor_model", ([], [], []), verbose=False).value


        self.model = model
        self.label_embedding = label_embedding
        self.scalar = scalar

        if self.is_initialized():
            print("[OK] ValuePredictor initialized successfully.")
        else:
            print("[ERROR] No ValuePredictor model available.")

    def initialize(self, model, label_embedding, scalar):
        self.model = model
        self.label_embedding = label_embedding
        self.scalar = scalar
        self.save()

    def is_initialized(self):
        return self.model

    def predict(self, data):
        feature_vectors = []
        for x in data:
            lat, lon, label = x
            embedded_label = self.label_embedding[label]
            feature_vector = [lat, lon] + embedded_label.tolist()
            feature_vectors.append(feature_vector)

        feature_vectors = self.scalar.transform(feature_vectors)
        predictions = self.model.predict(feature_vectors)

        return predictions

    def predict_single(self, lat, lon, label):
        x = self.predict([(lat, lon, label)])[0]
        return x

    def save(self):
        Cache("value_predictor_model", (self.model, self.label_embedding, self.scalar)).save()
