import preprocessing
from backend.code.location_recommender import LocationRecommender


def run():
    companies = preprocessing.get_companies()

    # use a small sample size for testing
    sample_size = 10
    recommender = LocationRecommender(companies, sample_size=sample_size)
    the_target = "dummy"
    recommender.set_target_tags([the_target])
    # format as specified in the google docs doc
    recommendations = recommender.get_attributed_location_recommendations(max_companies=10)
    # TODO: setup HTTP GET endpoint here Endpoints we need:
    #  1. GET /sectors
    #  returns all sectors, i.e. returns a list of strings
    #  2. GET /recommendations?sectors=...&max_companies=...
    #  returns the recommendations for the given sectors and max_companies, i.e. returns a list of Company objects)


if __name__ == '__main__':
    set(['A', 'B', 'C'])
    #run()
