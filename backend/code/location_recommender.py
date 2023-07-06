import random
import time
from typing import List

from geopy.distance import geodesic

from backend.code import config
from backend.code.cache import Cache
from backend.code.company import Company, CompanyType
from backend.code.value_predictor import ValuePredictor

# BoundingBox could be made a class in the future.
# Rectangular bounds of Germany
GERMANY_LAT_MIN = 47.2701
GERMANY_LAT_MAX = 55.0991
GERMANY_LON_MIN = 5.8663
GERMANY_LON_MAX = 15.0419

# Rectangular bounds of Saarland
SAARLAND_LAT_MIN = 49.1769
SAARLAND_LAT_MAX = 49.657
SAARLAND_LON_MIN = 6.2032
SAARLAND_LON_MAX = 7.5014


class LocationRecommender:
    """
    Recommends locations for a company based on the locations of companies with given tags.
    """

    def __init__(self, companies: List[Company], sample_size: int = 100000, download_model=True):
        """
        :param companies: All companies in the dataset, which influence the value of a founding location.
        :param sample_size: How many Monte Carlo samples to use for the recommendations.
        :param download_model: If True, download the model from the cloud. If False, use a self trained model.
        """
        self.companies = companies
        self.target_tags = []
        self.targets = []

        # How far recommendations should be apart from each other.
        # 𝛿-distinctiveness in the paper
        self.min_recommendation_distance = 20  # km

        # If calling get_detailed_location_recommendations,
        # the radius of the detailed view, i.e. where target companies are displayed, too.
        self.display_radius = 1  # in km

        self.sample_size = sample_size
        self.miss_time = 0

        self.hits = 0
        self.misses = 0

        self.M = 30

        # If True, only consider companies in Saarland, otherwise consider all companies in Germany.
        self.saarland_only = False

        # The predictor for the value of a founding location.
        # If available, we use MLP assisted Monte Carlo. Otherwise, we use the simple Monte Carlo.
        self.value_predictor: ValuePredictor = ValuePredictor(download_model=download_model)
        if not self.value_predictor.is_initialized():
            # Speedup Monte Carlo by caching distances and values.
            self.cache = Cache("distances", {})
            self.distances = self.cache.value
            self.value_cache = Cache("values", {})
            self.values = self.value_cache.value
        else:
            self.distances = {}

    def set_target_tags(self, target_tags: List[str]):
        """
        Sets the target tags, i.e. sectors of companies that are considered for the recommendations.
        :param target_tags: The list of target tags.
        """
        self.target_tags = target_tags
        # all companies that have at least one of the target tags
        self.targets = [company for company in self.companies if set(company.tags).intersection(set(target_tags))]
        print("Found", len(self.targets), "target companies")

    def set_detailed_view_radius(self, radius: int):
        """
        Sets the radius of the detailed view, i.e. where target companies are displayed, too.
        :param radius: The radius in km.
        """
        self.display_radius = radius

    def set_min_recommendation_distance(self, distance: int):
        """
        Sets the minimum distance between recommendations (𝛿-distinctiveness).
        :param distance: The minimum distance in km.
        """
        self.min_recommendation_distance = distance

    def set_saarland_only(self, saarland_only: bool):
        """
        If True, only consider companies in Saarland, otherwise consider all companies in Germany.
        :param saarland_only: Boolean flag.
        """
        self.saarland_only = saarland_only

    def set_M(self, M: int):
        """
        Sets the maximum distance in km to consider for the value of a founding location.
        :param M: The maximum distance in km.
        """
        self.M = M

    def value(self, recommended_company, target_company: Company = None) -> float:
        """
        Calculates the value of the founding location of a company.
        :param recommended_company: The company for which the value of the founding location is calculated.
        :param target_company: If given, we only calculate how much value the target company contributes.
        :return: The value of the founding location.
        """
        # For the value of the cluster (= value of the founding location),
        # we sum up the values each target company contributes.
        if target_company is None:
            # If we have a value predictor, use it instead of calculating the value explicitly.
            if self.value_predictor.is_initialized():
                return self.value_predictor.predict_single(*recommended_company.get_lat_long(), self.targets[0].tags[0])

            # Check if the value is already cached.
            if (recommended_company.get_lat_long(), self.targets[0].tags[0]) in self.values:
                self.value_cache.hit()
                return self.values[recommended_company.get_lat_long(), self.targets[0].tags[0]]

            # If not, calculate it.
            start = time.time()
            values = [self.value(recommended_company, target) for target in self.targets]
            self.miss_time += time.time() - start
            value = sum(values)
            self.values[recommended_company.get_lat_long(), self.targets[0].tags[0]] = value
            self.value_cache.miss()
            return value

        # Calculate the value a single target company contributes.
        # Depends on the vicinity (relative distance in relation to M)
        # and the potential (currently fixed to 1) of the target company.
        value = self.vicinity(recommended_company, target_company) * self.potential(target_company)
        return value

    def vicinity(self, origin_company: Company, target_company: Company = None) -> float:
        """
        Calculates the vicinity of a target company in relation to the origin company.
        :note: That the result depends on the maximum distance ```M```.
        :param origin_company: The origin company.
        :param target_company: The target company.
        :return: The vicinity of the target company in relation to the origin company.
        """
        M = self.M  # maximum distance in km
        vicinity = max((M - self.distance(origin_company, target_company)) / M, 0)
        return vicinity

    def distance(self, company1: Company, company2: Company) -> float:
        """
        Calculates the straight line distance between two companies.
        :param company1: The first company.
        :param company2: The second company.
        :return: The distance between the two companies.
        """
        # Create coordinate tuples

        coordinate1 = (company1.latitude, company1.longitude)
        coordinate2 = (company2.latitude, company2.longitude)

        # Check if distance is already cached
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
        """
        Defines the potential of a company, i.e. how much value it can contribute for a company founded nearby.
        :param company: The company to calculate the potential for.
        :return: The potential of the company.
        :note: Potential is currently fixed to 1.
        """
        return 1

    def get_random_point_in_germany(self):
        """
        Generates a random point in the rectangular bounding box of Germany.
        :return: A random point in the bounding box of Germany.
        :note: The point is not necessarily in Germany.
        """
        # Generate random latitude and longitude
        if self.saarland_only:
            latitude = random.uniform(SAARLAND_LAT_MIN, SAARLAND_LAT_MAX)
            longitude = random.uniform(SAARLAND_LON_MIN, SAARLAND_LON_MAX)
        else:
            latitude = random.uniform(GERMANY_LAT_MIN, GERMANY_LAT_MAX)
            longitude = random.uniform(GERMANY_LON_MIN, GERMANY_LON_MAX)

        latitude = config.rounding_policy(latitude)
        longitude = config.rounding_policy(longitude)

        # API call is too expensive, another verification method is needed.
        # if not self.is_in_germany(latitude, longitude):
        #     return self.get_random_point_in_germany()

        return latitude, longitude

    def get_random_possible_company_location(self):
        """
        Generates a random company location in Germany.
        :return: The random company at a random location in Germany.
        """
        latitude, longitude = self.get_random_point_in_germany()
        company = Company(latitude=latitude, longitude=longitude, type=CompanyType.RECOMMENDATION)
        return company

    def get_random_possible_company_locations(self, n: int):
        """
        Generates a list of random company locations in Germany.
        :param n: The number of random companies at random locations to generate.
        :return: The list of random companies at random locations in Germany.
        """
        recommendations = []
        for _ in range(n):
            recommendations.append(self.get_random_possible_company_location())
        return recommendations

    def get_location_recommendations(self, max_companies: int):
        """
        Generates a list of founding location recommendations.
        :param max_companies: The maximum number of recommendations to generate.
        :return: The list of recommendations (as Company objects).
        """

        SAMPLING_SIZE = self.sample_size
        print()
        print(f"Performing location recommendations (max: {max_companies}) using {SAMPLING_SIZE} monte carlo samples.")

        # Sample locations
        sampled_locations = self.get_random_possible_company_locations(SAMPLING_SIZE)

        # Calculate values for sampled locations
        for company in sampled_locations:
            company.value = self.value(company)

        # Sort sampled locations by value
        sampled_locations.sort(key=lambda x: x.value, reverse=True)

        recommendations = []

        # Repeat until max_companies recommendations are found.
        for _ in range(max_companies):
            if len(sampled_locations) == 0:
                break

            print("Sampled locations:", len(sampled_locations), end="\r")

            # Find the best recommendation
            best_recommendation = sampled_locations[0]

            # Add the best recommendation to the list of recommendations
            recommendations.append(best_recommendation)

            found_next_best = False

            # Remove samples that are too close to the best recommendation
            # Does not remove all samples, but only up to the point that
            # the first element of the ordered list is not too close.
            # Thus, this first element is the next best recommendation.
            next_sampled_locations = []
            total = 0
            for company in sampled_locations:
                total += 1
                if not found_next_best:
                    not_too_close = True
                    for recommendation in recommendations:
                        if self.distance(recommendation, company) <= self.min_recommendation_distance:
                            not_too_close = False
                            break
                    if not_too_close:
                        found_next_best = True
                if found_next_best:
                    next_sampled_locations.append(company)

            sampled_locations = next_sampled_locations

        # If we use regular Monte Carlo sampling, print the cache report.
        if not self.value_predictor.is_initialized():
            # self.cache.save()
            self.value_cache.save()
            self.value_cache.report()
            print(f"Cache hits: {self.hits / (self.hits + self.misses) * 100}%")
            print(f"recommendation: {[str(r) for r in recommendations]}")
            print(f"miss time: {self.miss_time}")

        return recommendations

    def get_attributed_location_recommendations(self, max_companies: int):
        """
        Generates a list of recommendations add adds the targets that are within the display radius as an attribute.
        :param max_companies: The maximum number of recommendations to generate.
        :return: The list of attributed recommendations (as Company objects).
        """
        recommendations = self.get_location_recommendations(max_companies)
        for recommendation in recommendations:
            recommendation.targets = [target for target in self.targets if
                                      self.distance(recommendation, target) <= self.display_radius]

        for recommendation in recommendations:
            print(self.value(recommendation))
        return recommendations

    def set_sample_size(self, sample_size: int):
        """
        Sets the sample size for the Monte Carlo sampling.
        :param sample_size: The new sample size.
        """
        self.sample_size = sample_size
