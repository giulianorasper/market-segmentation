import random
import time

from backend.code import preprocessing, config
from backend.code.location_recommender import LocationRecommender


def generate():
    """
    Generates a training set for the location recommender.
    Values are stored in the normal values cache.
    This method is just for automizing queries to the recommender.
    """
    companies = preprocessing.get_companies(config.companies_path)

    labels = []

    # Collect all available labels (sector names)
    for company in companies:
        for tag in company.tags:
            if tag not in labels:
                labels.append(tag)

    # Create a location recommender
    recommender = LocationRecommender(companies, download_model=False)
    recommender.set_sample_size(100)

    time_taken = 0
    start = time.time()

    # Generate samples for a given amount of hours.
    hours = 3
    _n_hours = 60 * 60 * hours

    # Request recommendations for each label, such that we get a balanced training set,
    # saved into the values cache.
    while time_taken < _n_hours:
        for target in labels:
            recommender.set_target_tags([target])
            recommendations = recommender.get_attributed_location_recommendations(max_companies=1)

        time_taken = time.time() - start
        print(f"Time taken: {time_taken / 60} minutes")
        print(f"Generated samples so far: {len(recommender.values)}")





if __name__ == '__main__':
    generate()