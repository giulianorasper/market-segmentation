from typing import List

from flask import Flask, request, jsonify, send_from_directory

import json
import backend.code.preprocessing as preprocessing
import backend.code.config as config
from backend.code.company import Company
from backend.code.location_recommender import LocationRecommender


app = Flask(__name__, static_url_path='/static')
companies = preprocessing.get_companies(config.companies_path)
sample_size = 10000
recommender = LocationRecommender(companies, sample_size=sample_size)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/save_parameters', methods=['POST'])
def get_recommendations():
    # Retrieve parameters from the request
    parameters = request.json
    """
    parameters that we get from javascript:
        "key": value,
        "yourCompany": our company's sector,
        "selectedTargetCompanies": target companies
        "saarlandOnly": if only saarland,
        "maxRecommendations": number of recommendations #PS: i think we need to change its name to min recommendations
        "detailsRadius": radius specified by client
    """
    
    print('Parameters printed: ', parameters)

    # Extract parameters
    the_target = parameters['selectedTargetCompanies']
    min_distance = 50
    radius = int(parameters['detailsRadius'])
    max_recommendations = int(parameters['maxRecommendations'])
    saarland_only = bool(parameters['saarlandOnly'])


    # use a small sample size for testing


    # Set the target tags, minimum distance, and radius
    recommender.set_saarland_only(saarland_only)
    recommender.set_target_tags(the_target)
    recommender.set_min_recommendation_distance(min_distance)
    recommender.set_detailed_view_radius(radius)

    # Get recommendations
    recommendations: List[Company] = recommender.get_location_recommendations(max_companies=max_recommendations)

    # Convert recommendations to JSON
    recommendations = [company.to_map() for company in recommendations]


    """
    recommendations should be in this format:
    {
        "geolocation": {
            "latitude": 123,
            "longitude": 321
        },
        "value": "42.33",
    }
    This returned to js and drawn on the map
    """
    recommendations2 = [{
        "geolocation": {
        "latitude": 51.3396,
        "longitude": 12.3713
      },
        },
           {
        "geolocation": {
        "latitude": 44.1396,
        "longitude": 18.3713
      },
        },
           {
        "geolocation": {
        "latitude": 42.3396,
        "longitude": 15.3713
      },
        },                 
    ]
        
    # Return recommendations as JSON response
    json_recommendations = json.dumps(recommendations, indent=4)
    print(json_recommendations)
    return json_recommendations

if __name__ == '__main__':
    app.run(debug=True)
    #set(['A', 'B', 'C'])
    #run()
