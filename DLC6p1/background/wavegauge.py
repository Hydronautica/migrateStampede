import numpy as np
import matplotlib.pyplot as plt

focusingTime = 0 
def read_surface_elevation(file_path):
    # Load the data
    X = np.loadtxt('./postProcessing/wavegauge/0/surfaceElevation.dat',skiprows=4)

    # Extract spatial coordinates and time
    time = X[3:, 0]
    x = X[0, 1:]
    y = X[1, 1:]
    z = X[2, 1:]

    # Extract instantaneous surface elevations
    eta = X[3:, 1:]

    # Eliminate times that are close to each other
    I = np.where(np.diff(time) < 1e-5)[0]
    time = np.delete(time, I + 1)
    eta = np.delete(eta, I + 1, axis=0)

    return time, x, y, z, eta

# Provide the path to the surfaceElevation.dat file
file_path = 'path/to/surfaceElevation.dat'

# Call the function to read the data
time, x, y, z, eta = read_surface_elevation(file_path)
time -= focusingTime
# Plot the data
plt.figure(figsize=(10, 6))
for i in range(len(x)):
    plt.plot(time, eta[:, i])

plt.xlabel('Time  [Relative to Focusing Time (s)]')
plt.ylabel('Eta (m)')
plt.title('Surface Elevation at Focusing Point')
#plt.legend()
plt.grid(True)

# Customize the appearance
plt.tight_layout()  # Ensure all elements are within the figure boundary
plt.tick_params(axis='both', which='both', labelsize=12)  # Adjust tick label font size
#plt.legend(fontsize=12)  # Adjust legend font size
plt.title('Surface Elevation at Focusing Point', fontsize=14)  # Adjust title font size

# Save the figure as a publication-quality image (e.g., PDF)
plt.savefig('surface_elevation_plot.pdf', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()
eta_column = eta[:, 0]
output_data = np.column_stack((time, eta_column))
np.savetxt('Medium_eta_values.txt', output_data, fmt='%10.5f', header='Time Eta')

