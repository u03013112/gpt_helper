import pandas as pd

df = pd.read_csv('/data/embedded/elephantfish_github.csv')
print(df['text'][32])