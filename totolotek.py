import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations

# Load the CSV file
df = pd.read_csv('dl.txt', sep=';', decimal=',')  # Make sure to replace 'your_file.csv' with your actual file path

# Split the 'numery' column into lists of numbers
df['numery'] = df['numery'].apply(lambda x: [int(num) for num in x.split(',')])

# Prepare a DataFrame for correlation analysis
all_numbers = [num for sublist in df['numery'] for num in sublist]
unique_numbers = sorted(set(all_numbers))
correlation_data = []

for numbers in df['numery']:
    row = [1 if num in numbers else 0 for num in unique_numbers]
    correlation_data.append(row)

correlation_df = pd.DataFrame(correlation_data, columns=unique_numbers, index=df['data'])

# Calculate the correlation matrix
correlation_matrix = correlation_df.corr()

# Find the pairs with the highest correlations
correlation_pairs = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates()

# Filter out self-correlations
correlation_pairs = correlation_pairs[correlation_pairs < 1]

# Get the top correlated pairs
top_pairs = correlation_pairs.head(15)  # You can adjust this number to get more or fewer top pairs

# Extract the numbers involved in the top correlated pairs
correlated_numbers = [num for pair in top_pairs.index for num in pair]

# Count the frequency of each number in the top pairs
number_counts = Counter(correlated_numbers)

# Select the 6 most common numbers (most correlated with each other)
most_correlated_numbers = [item[0] for item in number_counts.most_common(6)]

# Output the result
print("The most correlated combination of 6 numbers is:", most_correlated_numbers)
