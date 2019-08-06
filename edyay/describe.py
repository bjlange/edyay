import pandas as pd

def make_description_table(df):
    # find representative row
    all_filled = df[(~ df.isna()).all(axis=1)]
    print(f'{len(df)} rows')
    if len(all_filled) > 0:
        example_row = all_filled.iloc[0]
    else:
        # need to get "most complete row" if none are all-complete
        raise NotImplementedError
        
    desc = pd.DataFrame(example_row)
    desc.columns = ['Example value']
    desc.index.name = 'Data column name'
    empty_and_na_pct = ((df.isna()) | (df == '')).astype(int).sum() / len(df)
    desc['% empty or missing values'] = empty_and_na_pct * 100.0
    
    desc.reset_index(level=0, inplace=True)
    desc['Question the data answers'] = ''
    desc['Notes'] = ''
    
    desc = desc[['Question the data answers','Example value',
                 '% empty or missing values','Data column name', 'Notes']]
    return desc