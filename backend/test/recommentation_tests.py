import random
import unittest
from typing import List, Tuple

from hypothesis import given, strategies as st, settings

from backend.code import preprocessing, config
from backend.code.company import CompanyType, Company
from backend.code.location_recommender import LocationRecommender


@st.composite
def company_strategy(draw):
    tags = draw(st.lists(st.text(), min_size=1, max_size=20))

    companies = draw(st.lists(
        st.builds(
            Company,
            name=st.text(),
            type=st.sampled_from([CompanyType.TARGET]),
            tags=st.sampled_from(tags),
            latitude=st.floats(min_value=-90, max_value=90),
            longitude=st.floats(min_value=-180, max_value=180)
        ),
        min_size=0,
        max_size=50
    ))

    target = draw(st.sampled_from(tags))

    return companies, target


class TestRecommendations(unittest.TestCase):
    """
    Tests the location recommender (crash tests).
    """

    @given(company_strategy(), st.integers(min_value=0, max_value=50))
    @settings(max_examples=50)
    def test_generated_no_crash(self, fuzz: Tuple[List[Company], str], max_companies):
        companies, target = fuzz
        recommender = LocationRecommender(companies)
        recommender.set_target_tags([target])
        recommendations = recommender.get_attributed_location_recommendations(max_companies=max_companies)

    def test_dataset_recommendation(self):
        companies = preprocessing.get_companies(config.companies_path)
        size = len(companies)
        id = random.randint(0, size-1)
        target = companies[id].tags[0]
        recommender = LocationRecommender(companies)
        recommender.set_target_tags([target])
        recommender.set_sample_size(10000)
        recommendations = recommender.get_location_recommendations(max_companies=50)
        print([(company.latitude, company.longitude) for company in recommendations])