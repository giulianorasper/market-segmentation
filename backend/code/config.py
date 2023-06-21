# In case of changing the table, increment the version number and change the name of the table here.
companies_table_to_load = "Preprocessed_Data_V2.xlsx"

# Don't touch
resources_path = "../resources/"
cache_path = "../cache/"
companies_path = resources_path + companies_table_to_load


# accuracy explained:
# 1: ~11km distance between samples
# 2: ~1km distance between samples
# 3: <1m distance between samples
def rounding_policy(x):
    return round(x, 1)
