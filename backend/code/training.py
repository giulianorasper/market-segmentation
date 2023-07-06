import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

from backend.code.cache import Cache
from tqdm import tqdm

from backend.code.value_predictor import ValuePredictor


def create_unit_vector(i, size):
    """
    Creates a unit vector of the given size with a 1 at the i-th position.
    :param i: The position of the 1.
    :param size: The size of the vector.
    :return: The unit vector.
    """
    # Create a zero-filled array of the desired size
    vector = np.zeros(size)

    # Set the i-th element to 1
    vector[i] = 1

    return vector


def run():
    """
    Runs the training and saves the model to the cache.
    """
    cache = Cache("values")

    X = []
    y = []

    labels = []

    # Collect all available labels (sector names)
    for key in cache.value.keys():
        pos, label = key
        if label not in labels:
            labels.append(label)

    label_embedding = {}

    # Create a unit vector for each label, which we use as label embedding.
    for i, label in enumerate(labels):
        label_embedding[label] = create_unit_vector(i, len(labels))

    # Load training data from the values cache, created when running regular Monte Carlo simulations
    # Split it into features (X) and labels (y).
    for key, value in cache.value.items():
        pos, label = key
        lat, lon = pos

        feature_vector = [lat, lon] + label_embedding[label].tolist()
        X.append(feature_vector)
        y.append(value)

    # Split the dataset into training and test set (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"Number of training samples: {len(X_train) * 0.9}")
    print(f"Number of validation samples: {len(X_train) * 0.1}")
    print(f"Number of test samples: {len(X_test)}")

    # Normalize the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Create an instance of the MLPClassifier
    hidden_layer_sizes = (200, 200, 200, 200)
    mlp = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, max_iter=10000, random_state=42, verbose=True,
                       early_stopping=True, learning_rate='adaptive', batch_size=1000, tol=1e-5)

    print(f"Network architecture: {X_test.shape[1]} -> {hidden_layer_sizes} -> 1")

    # Train the model
    mlp.fit(X_train, y_train)

    # Plot the loss over iterations
    plt.figure(figsize=(8, 5))
    plt.plot(mlp.loss_curve_)
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.title('Loss Curve')
    plt.show()

    # Plot the loss over iterations
    plt.figure(figsize=(8, 5))
    plt.plot(mlp.validation_scores_)
    plt.xlabel('Iteration')
    plt.ylabel('R2 Score')
    plt.title('R2 Score Curve')
    plt.show()

    # Calculate the R2 score on the test set
    score = mlp.score(X_test, y_test)
    print(f"R2 score (test): {score}")

    # Save the model to the cache
    value_predictor = ValuePredictor()
    # Note: we save the scaler, to apply the same normalization to the input data during inference.
    value_predictor.initialize(mlp, label_embedding, scaler)


if __name__ == '__main__':
    run()
