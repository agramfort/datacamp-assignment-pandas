"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    return regions.drop(columns=['slug', 'id']).rename(columns={'code':'code_reg', 
                'name': 'name_reg'}).merge(departments.drop(columns=['id', 'slug']).rename(columns={'region_code': 'code_reg', 
                'name': 'name_dep', 'code': 'code_dep'}), on='code_reg', how='right')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    regions_and_departments['Department code'] = regions_and_departments['code_dep']
    for i in range(1, 10):
        regions_and_departments = regions_and_departments.replace('0{}'.format(i), str(i))

    return regions_and_departments.merge(referendum, on='Department code', how='right').dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    couples = set([(i[0], i[1]) for i in referendum_and_areas[['code_reg', 'name_reg']].values])
    referendum_and_areas = referendum_and_areas[['code_reg', 'Registered', 'Abstentions', 
                                                    'Null', 'Choice A', 'Choice B']].groupby(['code_reg'], as_index=True).sum()
    referendum_and_areas['name_reg'] = referendum_and_areas.index
    for code, name in couples:
        referendum_and_areas = referendum_and_areas.replace(code, name)

    return referendum_and_areas[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions = gpd.read_file('data/regions.geojson')

    regions = regions.rename(columns={'code': 'code_reg'})

    referendum_and_areas['rate A'] = referendum_and_areas['Choice A'] / (referendum_and_areas['Choice A'] + referendum_and_areas['Choice B'])

    output = gpd.GeoDataFrame(referendum_and_areas.merge(regions, on='code_reg', how='right').dropna()[['code_reg', 'name_reg', 'geometry']])

    output.plot('rate A')

    return output

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
