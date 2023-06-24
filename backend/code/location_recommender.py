import random
import time
from typing import List

from geopy import Nominatim
from geopy.distance import geodesic

from backend.code import config
from backend.code.cache import Cache
from backend.code.company import Company, CompanyType
from backend.code.value_predictor import ValuePredictor

GERMANY_LAT_MIN = 47.2701
GERMANY_LAT_MAX = 55.0991
GERMANY_LON_MIN = 5.8663
GERMANY_LON_MAX = 15.0419


class LocationRecommender:
    def __init__(self, companies: List[Company], sample_size: int = 100000):
        self.companies = companies
        self.target_tags = []
        self.targets = []
        self.min_recommendation_distance = 50 # km
        self.display_radius = 1 # km

        self.sample_size = sample_size
        self.miss_time = 0

        self.hits = 0
        self.misses = 0

        self.value_predictor: ValuePredictor = ValuePredictor()
        if not self.value_predictor.is_initialized():
            self.cache = Cache("distances", {})
            self.distances = self.cache.value
            self.value_cache = Cache("values", {})
            self.values = self.value_cache.value
        else:
            self.distances = {}

    def set_target_tags(self, target_tags: List[str]):
        self.target_tags = target_tags
        # all companies that have at least one of the target tags
        self.targets = [company for company in self.companies if set(company.tags).intersection(set(target_tags))]
        print("Found", len(self.targets), "target companies")

    def set_detailed_view_radius(self, radius: int):
        self.display_radius = radius

    def set_min_recommendation_distance(self, distance: int):
        self.min_recommendation_distance = distance

    def value(self, recommended_company, target_company: Company = None) -> float:
        # if we want to know the general value,
        # we just sum up the value of each potential target companies
        if target_company is None:
            if self.value_predictor.is_initialized():
                return self.value_predictor.predict_single(*recommended_company.get_lat_long(), self.targets[0].tags[0])

            if (recommended_company.get_lat_long(), self.targets[0].tags[0]) in self.values:
                self.value_cache.hit()
                return self.values[recommended_company.get_lat_long(), self.targets[0].tags[0]]
            start = time.time()
            values = [self.value(recommended_company, target) for target in self.targets]
            self.miss_time += time.time() - start
            value = sum(values)
            self.values[recommended_company.get_lat_long(), self.targets[0].tags[0]] = value
            self.value_cache.miss()
            return value

        value = self.vicinity(recommended_company, target_company) * self.potential(target_company)
        return value

    def vicinity(self, origin_company: Company, target_company: Company = None) -> float:
        M = 1000  # hard coded maximum distance in km
        vicinity = max((M - self.distance(origin_company, target_company)) / M, 0)
        return vicinity

    def distance(self, company1: Company, company2: Company) -> float:
        # Create coordinate tuples

        coordinate1 = (company1.latitude, company1.longitude)
        coordinate2 = (company2.latitude, company2.longitude)

        if (coordinate1, coordinate2) in self.distances:
            self.hits += 1
            return self.distances[(coordinate1, coordinate2)]
        if (coordinate2, coordinate1) in self.distances:
            self.hits += 1
            return self.distances[(coordinate2, coordinate1)]


        # Calculate distance using geodesic distance
        distance = geodesic(coordinate1, coordinate2).kilometers

        self.distances[(coordinate1, coordinate2)] = distance
        self.misses += 1

        return distance

    def potential(self, company: Company):
        # one could define how much potential a company has
        return 1

    def is_in_germany(self, latitude, longitude):
        geolocator = Nominatim(user_agent="my-app")  # Create a geolocator object
        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)  # Perform reverse geocoding

        if location is not None:
            country = location.raw['address'].get('country')  # Extract the country information
            return country == 'Germany'

        return False

    def get_random_point_in_germany(self):
        # Generate random latitude and longitude
        latitude = random.uniform(GERMANY_LAT_MIN, GERMANY_LAT_MAX)
        longitude = random.uniform(GERMANY_LON_MIN, GERMANY_LON_MAX)

        latitude = config.rounding_policy(latitude)
        longitude = config.rounding_policy(longitude)

        # if not self.is_in_germany(latitude, longitude):
        #     return self.get_random_point_in_germany()

        return latitude, longitude


    def get_random_possible_company_location(self):
        latitude, longitude = self.get_random_point_in_germany()
        company = Company(latitude=latitude, longitude=longitude, type=CompanyType.RECOMMENDATION)
        return company

    def get_random_possible_company_locations(self, n: int):
        recommendations = []
        for _ in range(n):
            recommendations.append(self.get_random_possible_company_location())
        return recommendations

    def get_location_recommendations(self, max_companies: int):

        SAMPLING_SIZE = self.sample_size
        print()
        print(f"Performing location recommendations (max: {max_companies}) using {SAMPLING_SIZE} monte carlo samples.")

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
            sampled_locations = [company for company in sampled_locations if self.distance(best_recommendation, company) >= self.min_recommendation_distance]
            print(f"Remaining samples: {len(sampled_locations)}")

        if not self.value_predictor.is_initialized():
            # self.cache.save()
            self.value_cache.save()
            self.value_cache.report()
            print(f"Cache hits: {self.hits / (self.hits + self.misses) * 100}%")
            print(f"recommendation: {[str(r) for r in recommendations]}")
            print(f"miss time: {self.miss_time}")
        return recommendations

    def get_attributed_location_recommendations(self, max_companies: int):
        recommendations = self.get_location_recommendations(max_companies)
        for recommendation in recommendations:
            recommendation.targets = [target for target in self.targets if self.distance(recommendation, target) <= self.display_radius]
        return recommendations

    def set_sample_size(self, sample_size: int):
        self.sample_size = sample_size


