import json
from enum import Enum
from typing import List


class CompanyType(Enum):
    RECOMMENDATION = 1,
    TARGET = 2,
    COMPETITOR = 3


class Company:

    def __init__(self, name: str = None, type: CompanyType = None, tags: List[str] = None, latitude: float = None, longitude: float = None):
        super().__init__()
        assert latitude is not None and longitude is not None, "latitude and longitude must be set"
        assert type is not None, "type must be set"


        # ATTRIBUTES PROVIDED BY THE DATASET
        self.name: str = name
        self.type: CompanyType = type
        # the tags of the company i.e. sectors
        self.tags: List[str] = tags
        self.latitude: float = latitude
        self.longitude: float = longitude
        # add more if needed...

        if self.name is None:
            self.name = "Unknown"
        if self.tags is None:
            self.tags: List[str] = []

        # ATTRIBUTES THAT ARE CALCULATED
        # meta information we might want to attach to the recommendation
        self.description: List[str] = None

        # the companies in the display radius that are targeted by the recommendation
        self.targets: List[Company] = None
        # color code given as HEX string
        self.color: str = None

        self.value: float = float('nan')

    def __str__(self):
        # print all attributes and their values
        return str(self.__dict__)

    def get_lat_long(self):
        return self.latitude, self.longitude

    def to_map(self):
        info = {
            "geolocation": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "value": self.value,
        }
        return info

#c = Company(name='ABC',type=1,tags=[],latitude=1.0,longitude=2.0)