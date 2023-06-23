import random
import time

from backend.code import preprocessing, config
from backend.code.location_recommender import LocationRecommender


def generate():
    companies = preprocessing.get_companies(config.companies_path)

    labels = []
    for company in companies:
        for tag in company.tags:
            if tag not in labels:
                labels.append(tag)

    recommender = LocationRecommender(companies)
    recommender.set_sample_size(1000)

    time_taken = 0
    start = time.time()

    hours = 8
    _n_hours = 60 * 60 * hours

    while time_taken < _n_hours:
        for target in labels:
            recommender.set_target_tags([target])
            recommendations = recommender.get_attributed_location_recommendations(max_companies=1)

        time_taken = time.time() - start
        print(f"Time taken: {time_taken / 60} minutes")
        print(f"Generated samples so far: {len(recommender.values)}")





if __name__ == '__main__':
    generate()