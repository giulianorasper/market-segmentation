# In case of changing the table, increment the version number and change the name of the table here.
import os.path

here = os.path.abspath(os.path.dirname(__file__))

companies_table_to_load = "companies_germany.xlsx"

# Don't touch
resources_path = os.path.join(here, "../resources/")
cache_path = os.path.join(here, "../cache/")
companies_path = resources_path + companies_table_to_load


# accuracy explained:
# 1: ~11km distance between samples
# 2: ~1km distance between samples
# 3: <1m distance between samples
def rounding_policy(x):
    return round(x, 3)
