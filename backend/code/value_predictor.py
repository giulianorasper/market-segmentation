import pickle

from backend.code.cache import Cache


class ValuePredictor:
    """
    A class which can predict the value of a given founding location and label (sector).
    """
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
        """
        Initializes the ValuePredictor with the given model, label embedding and scalar.
        :param model: The model to use for prediction.
        :param label_embedding: The label embedding to use for prediction.
        :param scalar: The scalar to use for normalization before prediction.
        :return:
        """
        self.model = model
        self.label_embedding = label_embedding
        self.scalar = scalar
        self.save()

    def is_initialized(self):
        """
        Checks if the ValuePredictor is initialized.
        :return: True if the ValuePredictor is initialized, False otherwise.
        """
        return self.model

    def predict(self, data):
        """
        Predicts the value of the given data.
        :param data: Tuple of (lat, lon, label) to predict the value for.
        :return: The predicted value.
        """
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
        """
        Predicts the value of founding a company at the given location with the given label.
        :param lat: The latitude of the founding location.
        :param lon: The longitude of the founding location.
        :param label: The label of the company.
        :return: The predicted value.
        """
        x = self.predict([(lat, lon, label)])[0]
        return x

    def save(self):
        """
        Saves the ValuePredictor to the cache.
        """
        Cache("value_predictor_model", (self.model, self.label_embedding, self.scalar)).save()
