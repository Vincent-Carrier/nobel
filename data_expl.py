# %% IMPORTS
import pandas as pd
import numpy as np
from pandas import Series, DataFrame

df: DataFrame = pd.read_json('nobel_winners/nwinners.json')
df.info()
df.describe()
df = df.sort_values('name')

# %% LOOK FOR DUPLICATES
df = df.drop_duplicates(['name', 'year'])
double_winners = df[['name', 'year', 'country', 'category']]
double_winners = double_winners[df.duplicated('name', keep=False)]
df.drop(df[(df.name == 'Ragnar Granit') & (df.year == 1809)].index,
        inplace=True)

# %% REMOVE CORRUPT YEAR DATA
for i in (355, 558, 559):
    df.loc[i, 'year'] = np.nan

# %%
df['award_age'] = df.year - pd.DatetimeIndex(df.date_of_birth).year
df = df.sort_values('award_age')

# %% INSERT INTO MONGODB
from pymongo import MongoClient
from pymongo.collection import Collection

client = MongoClient()
db = client.nobel_prize
coll: Collection = db.winners

coll.insert_many(df.to_dict('records'))
