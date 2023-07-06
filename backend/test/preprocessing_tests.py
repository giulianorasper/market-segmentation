import unittest
from hypothesis import given, strategies as st, assume

from backend.code import preprocessing


class TestProprocessing(unittest.TestCase):
    """
    Tests the preprocessing module.
    """

    @given(st.lists(st.floats(), min_size=2, max_size=2))
    def test_string_to_tuple(self, coordinates):
        """
        Tests the string_to_tuple function.
        """
        lat = coordinates[0]
        lon = coordinates[1]

        assume(-90 <= lat <= 90)
        assume(-180 <= lon <= 180)

        input_string = "(" + str(lat) + ", " + str(lon) + ")"

        lat_rs, lon_rs = preprocessing.string_to_tuple(input_string)
        assert lat == lat_rs
        assert lon == lon_rs