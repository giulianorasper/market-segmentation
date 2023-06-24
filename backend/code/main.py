from typing import List

import preprocessing
from backend.code.company import Company
from backend.code.location_recommender import LocationRecommender


def run():
    companies = preprocessing.get_companies(config.companies_path)

    # use a small sample size for testing
    sample_size = 10
    recommender = LocationRecommender(companies, sample_size=sample_size)
    the_target = "dummy"
    # the labels of sectors which are considered as target sectors
    recommender.set_target_tags([the_target])
    # the minimum distance between two recommendations
    recommender.set_min_recommendation_distance(10)
    # the radius of the detailed view
    recommender.set_detailed_view_radius(10)
    # the recommendations (limited to max_companies)
    # the target companies in the display radius are contained in the targets attribute of each recommendation
    recommendations: List[Company] = recommender.get_attributed_location_recommendations(max_companies=10)
    # TODO: setup HTTP GET endpoint here Endpoints we need:
    #  1. GET /sectors
    #  returns all sectors, i.e. returns a list of strings
    #  2. GET /recommendations?sectors=...&max_companies=...
    #  returns the recommendations for the given sectors and max_companies, i.e. returns a list of Company objects)


if __name__ == '__main__':
    set(['A', 'B', 'C'])
    #run()
