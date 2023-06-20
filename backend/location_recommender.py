import copy
import random
from typing import List

from geopy.distance import geodesic

from company import Company

GERMANY_LAT_MIN = 47.2701
GERMANY_LAT_MAX = 55.0991
GERMANY_LON_MIN = 5.8663
GERMANY_LON_MAX = 15.0419


class LocationRecommender:
    def __init__(self, companies: List[Company]):
        self.companies = companies
        self.target_tags = []
        self.targets = []
        self.min_recommendation_distance = 1 # km
        self.display_radius = 1 # km

    def set_target_tags(self, target_tags: List[str]):
        self.target_tags = target_tags
        # all companies that have at least one of the target tags
        self.targets = [company for company in self.companies if set(company.tags).intersection(set(target_tags))]

    def value(self, recommended_company, target_company: Company = None) -> float:
        # if we want to know the general value,
        # we just sum up the value of each potential target companies
        if target_company is None:
            values = [self.value(recommended_company, target) for target in self.targets]
            return sum(values)

        return self.vicinity(recommended_company, target_company) * self.potential(target_company)

    def vicinity(self, origin_company: Company, target_company: Company = None) -> float:
        M = 1000  # how far we expect the farthest possible recommendation point to be
        return (M - self.distance(origin_company, target_company)) / M

    def distance(self, company1: Company, company2: Company) -> float:
        # Create coordinate tuples
        coordinate1 = (company1.latitude, company1.longitude)
        coordinate2 = (company2.latitude, company2.longitude)

        # Calculate distance using geodesic distance
        distance = geodesic(coordinate1, coordinate2).kilometers
        return distance

    def potential(self, company: Company):
        # one could define how much potential a company has
        return 1



    def is_inside_germany(self, latitude: float, longitude: float) -> bool:
        # Check latitude range
        if not (GERMANY_LAT_MIN <= latitude <= GERMANY_LAT_MAX):
            return False

        # Check longitude range
        if not (GERMANY_LON_MIN <= longitude <= GERMANY_LON_MAX):
            return False

        return True

    def get_random_point_in_germany(self):
        # Generate random latitude and longitude
        latitude = random.uniform(GERMANY_LAT_MIN, GERMANY_LAT_MAX)
        longitude = random.uniform(GERMANY_LON_MIN, GERMANY_LON_MAX)

        return latitude, longitude


    def get_random_possible_company_location(self):
        latitude, longitude = self.get_random_point_in_germany()
        company = Company(latitude=latitude, longitude=longitude, type=Company.Type.RECOMMENDATION)
        return company

    def get_random_possible_company_locations(self, n: int):
        recommendations = []
        for _ in range(n):
            recommendations.append(self.get_random_possible_company_location())
        return recommendations

    def get_location_recommendations(self, max_companies: int):
        SAMPLING_SIZE = 10000
        sampled_locations = self.get_random_possible_company_locations(SAMPLING_SIZE)
        recommendations = []

        for _ in range(max_companies):
            if len(sampled_locations) == 0:
                break

            # Find the best recommendation
            best_recommendation = max(sampled_locations, key=lambda company: self.value(company))

            # Add the best recommendation to the list of recommendations
            recommendations.append(best_recommendation)

            # Remove samples that are too close to the best recommendation
            sampled_locations = [company for company in sampled_locations if self.value(company) >= self.min_recommendation_distance]

        return recommendations

    def get_attributed_location_recommendations(self, max_companies: int):
        recommendations = self.get_location_recommendations(max_companies)
        for recommendation in recommendations:
            recommendation.targets = [target for target in self.targets if self.distance(recommendation, target) <= self.display_radius]
        return recommendations

