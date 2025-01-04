import pandas as pd

# Load the CSV file
file_path = "acorn_socio_economic_classification.csv"  # Update this path to where the file is located
df = pd.read_csv(file_path)

# Create unique values for 'Category-Group'
df['Category-Group'] = df['Category'] + "-" + df['Group']

# Extract unique values
unique_category_group = df['Category-Group'].unique()

# Display the unique values
print("Unique Category-Group combinations:")
for value in unique_category_group:
    print(value)

# Save to a new CSV if needed
output_path = "acorn_socio_economic_classification_level1_2.csv"
pd.DataFrame({'Category-Group': unique_category_group}).to_csv(output_path, index=False)
print(f"Unique Category-Group combinations saved to {output_path}")
