from typing import List

from company import Company

import pandas as pd #PR: pandas needed to extract data from xlsx file


def get_companies(filepath:str) -> List[Company]: #PR added filepath to dataset.xlsx file
    """
    This function reads the companies from the dataset and return them as a list of Company objects.
    :return: The list of companies contained in the dataset.
    """
    # TODO: Implement data preprocessing here

    #Reading the dataset file
    df = pd.read_excel(filepath)
    res = []

    #Iterating over dataset to create Company objects and put them in a list
    for index,row in df.iterrows():
        c = Company(name=row['Company Name 1'],
                    type = 2,    #not 100% if the type is right
                    tags=[row['Branchencode1']],
                    latitude=row['PLZ_Coordinates'][0],
                    longitude = row['PLZ_Coordinates'][1])
        res.append(c)
    
    return res
