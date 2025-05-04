
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(os.getenv('NEON_DB_URL'))

def fetch_data_from_postgres(year=None, area=None, crime_category=None, gender=None, descent=None, part=None):
    query = "SELECT * FROM la_crime_data WHERE TRUE"
    params = {}

    if year:
        query += " AND DATE_TRUNC('year', date_rptd) = %(year)s"
        params['year'] = f"{year}-01-01"
    if area:
        query += " AND area_name = %(area)s"
        params['area'] = area
    if crime_category:
        query += " AND crime_cat = %(crime_category)s"
        params['crime_category'] = crime_category
    if gender:
        query += " AND vict_sex = %(gender)s"
        params['gender'] = gender
    if descent:
        query += " AND vict_descent = %(descent)s"
        params['descent'] = descent
    if part:
        query += " AND part_1_2 = %(part)s"
        params['part'] = part

    df = pd.read_sql(query, engine, params=params, parse_dates=["datetime"])
    return df.set_index("datetime")



def fetch_filter_options():
    df = pd.read_sql("SELECT DISTINCT EXTRACT(YEAR FROM date_rptd) AS year FROM la_crime_data", engine)
    years = sorted(df['year'].dropna().astype(int).unique())

    df2 = pd.read_sql("SELECT DISTINCT area_name FROM la_crime_data", engine)
    areas = df2['area_name'].dropna().unique()

    df3 = pd.read_sql("SELECT DISTINCT crime_cat FROM la_crime_data", engine)
    crime_categories = df3['crime_cat'].dropna().unique()

    df4 = pd.read_sql("SELECT DISTINCT vict_sex FROM la_crime_data", engine)
    genders = df4['vict_sex'].dropna().unique()

    df5 = pd.read_sql("SELECT DISTINCT vict_descent FROM la_crime_data", engine)
    descents = df5['vict_descent'].dropna().unique()

    return years, areas, crime_categories, genders, descents
