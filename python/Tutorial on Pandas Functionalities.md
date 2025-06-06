# Tutorial on pandas functionalities: json_normalize, record_path, meta, and merge

## 1. json_normalize

pd.json_normalize is a powerful function in pandas used to flatten nested JSON data into a tabular format (DataFrame). It allows you to extract deeply nested elements while keeping associated metadata.
Example:

```
import pandas as pd

data = [
    {
        "id": 1,
        "name": "Alice",
        "address": {"city": "New York", "zip": "10001"},
        "hobbies": [{"hobby": "reading"}, {"hobby": "cycling"}]
    },
    {
        "id": 2,
        "name": "Bob",
        "address": {"city": "Los Angeles", "zip": "90001"},
        "hobbies": [{"hobby": "gaming"}, {"hobby": "swimming"}]
    }
]

df = pd.json_normalize(data)
print(df)
```

Output:
```
   id   name address.city address.zip                          hobbies
0   1  Alice    New York       10001  [{'hobby': 'reading'}, {'hobby': 'cycling'}]
1   2    Bob  Los Angeles       90001  [{'hobby': 'gaming'}, {'hobby': 'swimming'}]
```

The function flattens the address dictionary but does not expand the hobbies list.


## 2. Understanding record_path and meta
**record_path**
- Used to extract data from a nested list of dictionaries.
- Creates multiple rows for each item in the list.
- Example: Extracting hobbies from the nested list.

**meta**
- Used to keep track of higher-level attributes (metadata) when extracting a nested list.
- Helps preserve relationships between extracted records and their parent records.

Example:

```
df_hobbies = pd.json_normalize(data, record_path=['hobbies'], meta=['id', 'name'])
print(df_hobbies)
```

Output:
```
      hobby  id   name
0  reading   1  Alice
1  cycling   1  Alice
2  gaming   2    Bob
3  swimming  2    Bob
```

- record_path=['hobbies'] extracts the list inside hobbies, creating a new row per item.
- meta=['id', 'name'] ensures that each extracted record retains its corresponding id and name.

## 3. pd.merge: Merging DataFrames

pd.merge combines two DataFrames based on common columns or index values.
Key parameters:
- how: Defines the merge type (inner, left, right, outer).
- left_on: Specifies the column in the left DataFrame for merging.
- right_on: Specifies the column in the right DataFrame for merging.
- suffixes: Adds suffixes to overlapping column names.
- indicator: If True, adds a column _merge showing the merge status (left_only, right_only, both).

Example:

```
df1 = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
df2 = pd.DataFrame({'id': [2, 3, 4], 'age': [25, 30, 35]})

df_merge = pd.merge(df1, df2, how='outer', on='id', suffixes=('_left', '_right'), indicator=True)
print(df_merge)
```

Output:
```
   id     name   age      _merge
0   1    Alice   NaN  left_only
1   2      Bob  25.0       both
2   3  Charlie  30.0       both
3   4      NaN  35.0  right_only
```
- how='outer' ensures all rows are included.
- suffixes=('_left', '_right') prevents column name conflicts.
- indicator=True shows the source of each row.

## 4. Breaking Down the Provided Code

```
df1 = pd.json_normalize(data)
df2 = pd.json_normalize(data, max_level=2, record_path=['financialCategories'], meta=['billId', 'installmentId', 'bankMovementId'])
df3 = pd.json_normalize(data, max_level=2, record_path=['departamentCosts'], meta=['billId', 'installmentId', 'bankMovementId'])
df4 = pd.json_normalize(data, max_level=2, record_path=['buldingCosts'], meta=['billId', 'installmentId', 'bankMovementId'])
dfmerge = pd.merge(df1, df2,  how='outer', left_on=['bankMovementId'], right_on=['bankMovementId'], suffixes=('', '_financial'), indicator=False)
```

Step-by-step breakdown:

- df1 = pd.json_normalize(data)
	Flattens the JSON into a tabular format.
	Expands nested dictionaries but not lists.

- df2, df3, and df4
	Extract financialCategories, departamentCosts, and buldingCosts (nested lists) into separate DataFrames.
	Use record_path to extract lists.
	Use meta to retain billId, installmentId, and bankMovementId (associating extracted records with their parent).

- dfmerge = pd.merge(df1, df2, how='outer', left_on=['bankMovementId'], right_on=['bankMovementId'], suffixes=('', '_financial'), indicator=False)
	Merges df1 and df2 on bankMovementId.
	how='outer' ensures all data is included.
	suffixes=('', '_financial') prevents column name conflicts.

