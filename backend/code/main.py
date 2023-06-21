import preprocessing

def run():
    companies = preprocessing.get_companies()
    recommender = LocationRecommender(companies)
    # TODO: setup HTTP GET endpoint here Endpoints we need:
    #  1. GET /sectors
    #  returns all sectors, i.e. returns a list of strings
    #  2. GET /recommendations?sectors=...&max_companies=...
    #  returns the recommendations for the given sectors and max_companies, i.e. returns a list of Company objects)


if __name__ == '__main__':
    set(['A', 'B', 'C'])
    #run()
