import re

import pandas as pd

df = pd.DataFrame(columns=['aa', 'bb'])
df['aa'] = [1, 2, 3, 4]
df['bb'] = [1, 2, 3, 4]
dic = {"aa": 5, 'bb': 5}
df.loc[df.shape[0]] = dic
print(df.shape[0])
print(df)


