import matplotlib.pyplot as plt

def plot_columns_from_file(file_path):
    # Read data from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize lists for first and fourth column data
    first_column = []
    fourth_column = []

    # Extract data from each line
    for line in lines:
        columns = line.strip().split(',')
        if len(columns) >= 4:
            first_column.append(float(columns[0]))
            fourth_column.append(float(columns[3]))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(first_column, fourth_column, marker='o')
    plt.xlabel('First Column')
    plt.ylabel('Fourth Column')
    plt.title('Plot of First Column against Fourth Column')
    plt.grid(True)
    plt.show()

# Example usage
plot_columns_from_file('data/centreOfMass.dat')  # Replace with your file path

