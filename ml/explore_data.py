"""
Step 1: Explore the dataset.

Before training ANY model, we need to understand what we're working
with — how many rows, what each column means, whether anything's
missing, and whether the thing we're predicting (target) is balanced.
Skipping this step is one of the most common beginner mistakes in ML —
you can build a model on data you don't understand and get numbers
that LOOK fine but are meaningless.

Run this with: python ml/explore_data.py
"""

import pandas as pd

# Load the dataset we saved locally.
df = pd.read_csv("ml/data/heart.csv")

print("=" * 60)
print("SHAPE (rows, columns)")
print("=" * 60)
print(df.shape)
# (303, 14) means 303 patients, 14 columns (13 features + 1 target)

print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)
print(df.columns.tolist())

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)
print(df.head())

print("\n" + "=" * 60)
print("DATA TYPES + MISSING VALUES")
print("=" * 60)
print(df.info())
# .info() shows the type of each column (int/float) and, importantly,
# whether any values are missing. "303 non-null" on every column
# means: no missing data. If a column showed e.g. "280 non-null",
# that would mean 23 rows are missing a value there — something
# we'd need to handle before training.

print("\n" + "=" * 60)
print("STATISTICAL SUMMARY (numeric columns)")
print("=" * 60)
print(df.describe())
# .describe() gives count/mean/std/min/max/quartiles for every
# numeric column — useful for spotting outliers or impossible values
# (e.g. if 'age' showed a min of -5 or max of 900, we'd know
# something is wrong with the data).

print("\n" + "=" * 60)
print("TARGET COLUMN BALANCE")
print("=" * 60)
print(df["target"].value_counts())
# This is important: 'target' is what we're predicting (1 = has
# heart disease, 0 = doesn't). If this were, say, 290 zeros and only
# 13 ones, that's a SEVERELY imbalanced dataset — a lazy model could
# get 95% "accuracy" by just always guessing 0, while being useless.
# We want to see something reasonably close to balanced.
