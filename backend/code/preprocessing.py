import os.path
import pickle
from typing import List

import config
from backend.code.company import Company, CompanyType

import pandas as pd  # PR: pandas needed to extract data from xlsx file


def get_companies(filepath: str) -> List[Company]:  # PR added filepath to dataset.xlsx file
    """
    This function reads the companies from the dataset and return them as a list of Company objects.
    :return: The list of companies contained in the dataset.
    """

    if not os.path.exists(config.dumps_path):
        os.makedirs(config.dumps_path)

    file_name = os.path.basename(filepath)

    dump_file_path = config.dumps_path + file_name + ".pkl"

    if os.path.exists(dump_file_path):
        print("Loading companies from dump...")
        with open(dump_file_path, 'rb') as file:
            obj = pickle.load(file)
        return obj

    # Reading the dataset file
    df = pd.read_excel(filepath)
    res = []

    # Iterating over dataset to create Company objects and put them in a list
    for index, row in df.iterrows():

        lat, lon = string_to_tuple(row['PLZ_Coordinates'])

        c = Company(name=row['Company Name 1'],
                    type=CompanyType.TARGET,  # by default, we assume that all companies are targets
                    tags=[row['Branchencode1']],
                    latitude=lat,
                    longitude=lon)
        res.append(c)

        break

    # Saving the list of companies to a dump file
    with open(dump_file_path, 'wb') as file:
        pickle.dump(res, file)

    return res


def string_to_tuple(input_string):
    # Remove parentheses and whitespace from the string
    cleaned_string = input_string.strip('() ')

    # Split the string into individual values
    values = cleaned_string.split(',')

    # Convert each value to float and create a tuple
    tuple_values = tuple(float(value) for value in values)

    return tuple_values
