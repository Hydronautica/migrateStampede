import math

# Function to calculate k_h and omega_h
def calculate_kh_omegah(k_waves, wave_height, omega_waves, water_depth):
    # Common calculation part
    common_part = math.sqrt((k_waves ** 2 * wave_height ** 2 * omega_waves ** 2) / 
                            (2.0 * water_depth * k_waves * math.tanh(k_waves * water_depth)))
    
    # Calculate k_h
    k_h = common_part * 2.71 * 0.1 * 1e-6

    # Calculate omega_h
    omega_h = common_part * 2.71

    return k_h, omega_h

# Function to get user input and calculate k_h and omega_h
def main():
    print("Enter the following values:")

    # Get user inputs
    k_waves = float(input("Wavenumber (k_waves): "))
    wave_height = float(input("Wave Height (wave_height): "))
    omega_waves = float(input("Wave Omega (omega_waves): "))
    water_depth = float(input("Water Depth (water_depth): "))
    

    # Calculate k_h and omega_h
    k_h, omega_h = calculate_kh_omegah(k_waves, wave_height, omega_waves, water_depth)

    # Display results
    print("\nTurbulent kinetic energy from waves (k_h):", k_h)
    print("Omega from waves (omega_h):", omega_h)

# Run the main function
if __name__ == "__main__":
    main()
