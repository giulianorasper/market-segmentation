import math
import os.path
import pickle
from typing import List

from backend.code import config
from backend.code.cache import Cache
from backend.code.company import Company, CompanyType

import pandas as pd  # PR: pandas needed to extract data from xlsx file


def get_companies(filepath: str) -> List[Company]:  # PR added filepath to dataset.xlsx file
    """
    This function reads the companies from the dataset and return them as a list of Company objects.
    :return: The list of companies contained in the dataset.
    """

    file_name = os.path.basename(filepath)

    # We use a cache to speed up the loading process
    # for the next time the program is run.
    cache = Cache(f"companies_{file_name}", [])
    res = cache.value

    if res:
        return res

    # We use a local dataset if available.
    # Otherwise, we download it from the huggingface hub.
    if os.path.isfile(filepath):
        print("[INFO] Using dataset from local file.")
    else:
        print("[INFO] Dataset not found locally. Downloading from huggingface hub...")
        from huggingface_hub import hf_hub_download

        REPO_ID = "grasper/market-segmentation"
        FILENAME = file_name

        filepath = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

    print("[INFO] The companies are loaded for the first time from the dataset. This may take about a minute...")
    print("[INFO] The next time you run the program, the companies will be loaded from the cache.")

    # Reading the dataset file
    df = pd.read_excel(filepath)

    # Iterating over dataset to create Company objects and put them in a list
    for index, row in df.iterrows():

        lat, lon = string_to_tuple(row['PLZ_Coordinates'])
        lat, lon = config.rounding_policy(lat), config.rounding_policy(lon)

        # verify that the coordinates are in valid range
        fail = False
        if math.isnan(lat) or math.isnan(lon):
            fail = True
        if lat < -90 or lat > 90:
            fail = True
        if lon < -180 or lon > 180:
            fail = True

        if fail:
            print(f"invalid coordinates for company {row['Company Name 1']} --> skipping")
            continue

        c = Company(name=row['Company Name 1'],
                    type=CompanyType.TARGET,  # by default, we assume that all companies are targets
                    tags=[row['CustomSector']],
                    latitude=lat,
                    longitude=lon)
        res.append(c)

    cache.save()

    return res


def string_to_tuple(input_string):
    """
    Converts a string of the form "(x,y)" to a tuple of floats (x,y)
    :param input_string: The string to convert.
    :return: The tuple of floats.
    """
    # Remove parentheses and whitespace from the string
    cleaned_string = input_string.strip('() ')

    # Split the string into individual values
    values = cleaned_string.split(',')

    # Convert each value to float and create a tuple
    tuple_values = tuple(float(value) for value in values)

    return tuple_values
