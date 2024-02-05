import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import re
import matplotlib.lines as mlines  # Import statement for mlines

# User-defined y-axis limits
y_min = -15.0  # Set your desired minimum y-value here
y_max = 15.0   # Set your desired maximum y-value here
x_max = 2200.0   # Set your desired maximum y-value here
time_step = 0.0282  # Duration of each time step in seconds
stride = 1        # Difference in index between successive frames
x_shift = 675          # OpenFOAM shift to OCW3D domain
gauge_distance = 5  # Distance between each wave gauge
# Function to extract data from a .bin file
def extract_data_from_file(filename):
    with open(filename, 'rb') as file:
        dummy = np.fromfile(file, dtype=np.int32, count=1)[0]
        Nx = np.fromfile(file, dtype=np.int32, count=1)[0]
        Ny = np.fromfile(file, dtype=np.int32, count=1)[0]
        dummy = np.fromfile(file, dtype=np.int32, count=1)[0]

        dummy = np.fromfile(file, dtype=np.int32, count=1)[0]
        X = np.fromfile(file, dtype=np.float64, count=Nx * Ny)
        Y = np.fromfile(file, dtype=np.float64, count=Nx * Ny)
        dummy = np.fromfile(file, dtype=np.int32, count=1)[0]

        dummy = np.fromfile(file, dtype=np.int32, count=1)[0]
        E = np.fromfile(file, dtype=np.float64, count=Nx * Ny)
    
    return X, Y, E

# Function to read and extract data from surfaceElevation.dat
def read_surface_elevation(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    times = []
    gauge_data = []
    for line in lines[1:]:  # Skip header
        parts = line.split()
        times.append(float(parts[0]))
        gauge_data.append([float(val) for val in parts[1:]])
    return np.array(times), np.array(gauge_data)

# Read surface elevation data
surface_elevation_file = 'postProcessing/waterline/0/surfaceElevation.dat'
times, gauge_data = read_surface_elevation(surface_elevation_file)

# Initialize plot
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2, label='OceanWave3D Waterline')  # Add label for legend
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Set a fixed color for all gauge markers
gauge_color = 'green'  # You can choose any color you prefer
gauge_lines = [ax.plot([], [], marker='.', linestyle='-', color=gauge_color)[0] for _ in range(gauge_data.shape[1])]

plt.xlabel('Position (m)')  # X-axis label
plt.ylabel('Water Elevation (m)')  # Y-axis label
plt.title('Nested Coupling Between OceanWave3D And OpenFOAM')  # Title


# Create legends for line and markers
line_legend = ax.legend(handles=[line], loc='upper right', bbox_to_anchor=(1.0, 1))
ax.add_artist(line_legend)
ax.add_artist(line_legend)

# Create a proxy artist for marker legend
# Use the same color as the gauge markers
marker_legend = mlines.Line2D([], [], color=gauge_color, marker='.', linestyle='-', label='OpenFOAM Waterline')
ax.legend(handles=[marker_legend], loc='upper right', bbox_to_anchor=(1.0, 0.915))
ax.add_artist(line_legend)
plt.grid(True)
plt.axis('normal')
ax.set_ylim(y_min, y_max)
ax.set_xlim(0, x_max)
# Function to update gauge data on the plot
def update_gauge_data(current_time):
    # Find closest time index in surface elevation data
    time_index = np.argmin(np.abs(times - current_time))
    for i, gl in enumerate(gauge_lines):
        scaled_x = gauge_distance * i + x_shift  # Scale and shift x-coordinate
        gl.set_data([scaled_x], [gauge_data[time_index, i]])


# Function to initialize the background of each frame
def init():
    line.set_data([], [])
    time_text.set_text('')
    for gl in gauge_lines:
        gl.set_data([], [])
    return [line, time_text] + gauge_lines
dirpath = './'

def save_wave_data(current_time, all_gauge_data):
    with open('wave_data.csv', 'a') as file:  # Open file in append mode
        data_str = ", ".join(map(str, all_gauge_data))  # Convert all gauge data to string
        file.write(f"{current_time}, {data_str}\n")
# Function to animate each frame
def animate(i):
    filename = f'EP_{i:05d}.bin'
    full_path = os.path.join(dirpath, filename)
    if os.path.exists(full_path):
        X, Y, E = extract_data_from_file(full_path)
        line.set_data(X, E)
        current_time = i * time_step * stride
        time_text.set_text(f'Time: {current_time:.2f}s')
        update_gauge_data(current_time)
        # Save the data for all gauges at the current time
        time_index = np.argmin(np.abs(times - current_time))
        save_wave_data(current_time, gauge_data[time_index])
    return [line, time_text] + gauge_lines

# Create list of file indices based on existing files in the directory and stride
file_indices = []
for file in os.listdir(dirpath):
    if re.match(r'EP_\d{5}\.bin', file):
        index = int(file[3:8])
        if index % stride == 0:
            file_indices.append(index)
file_indices.sort()

# Create animation
ani = animation.FuncAnimation(fig, animate, frames=file_indices, init_func=init, blit=True)

# Save the animation
ani.save('wave_animation.mp4', fps=5, extra_args=['-vcodec', 'libx264'],dpi=600)

plt.show()
