import random
from collections import defaultdict

from backend.code import preprocessing, config
from backend.code.location_recommender import LocationRecommender


def calculate_variance_between_lists(list1, list2):
    # Check if the lists have the same length
    if len(list1) != len(list2):
        raise ValueError("The two lists must have the same length.")

    # Calculate the mean of each coordinate separately
    mean_x1 = sum(point[0] for point in list1) / len(list1)
    mean_y1 = sum(point[1] for point in list1) / len(list1)
    mean_x2 = sum(point[0] for point in list2) / len(list2)
    mean_y2 = sum(point[1] for point in list2) / len(list2)

    # Calculate the squared differences for each coordinate
    squared_diffs_x = [(point[0] - mean_x2) ** 2 for point in list1]
    squared_diffs_y = [(point[1] - mean_y2) ** 2 for point in list1]

    # Calculate the average of the squared differences (variance)
    variance = (sum(squared_diffs_x) + sum(squared_diffs_y)) / len(list1)

    return variance
def run():
    companies = preprocessing.get_companies(config.companies_path)

    labels = []
    for company in companies:
        for tag in company.tags:
            if tag not in labels:
                labels.append(tag)

    print(f"Number of labels: {len(labels)}")

    recommender = LocationRecommender(companies)
    results = defaultdict(list)

    for label in labels:
        recommender.set_target_tags([label])

        current = 1000
        end = 1000000
        step = 1000
        while current < end:

            if current + step * 2 >= end:
                current = end

            recommender.set_sample_size(current)
            recommendations = recommender.get_attributed_location_recommendations(max_companies=1, )
            best_company = recommendations[0]
            lat, lon = best_company.latitude, best_company.longitude
            results[current].append((lat, lon))

            current += step
            step = step * 2

    for key in results:
        print(key, calculate_variance_between_lists(results[key], results[end]))












    current += step
    step = step * 2

    # for label in labels:
    #     recommender = LocationRecommender(companies)
    #     recommender.set_target_tags([label])
    #     recommendations = recommender.get_attributed_location_recommendations(max_companies=1)



if __name__ == '__main__':
    run()