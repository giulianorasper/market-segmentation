from backend.code.cache import Cache


class ValuePredictor:
    def __init__(self):
        model, label_embedding, scalar = Cache("value_predictor_model", ([], [], [])).value
        self.model = model
        self.label_embedding = label_embedding
        self.scalar = scalar
        if not self.is_initialized():
            print("Value predictor model not found. Please train the model first.")

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
