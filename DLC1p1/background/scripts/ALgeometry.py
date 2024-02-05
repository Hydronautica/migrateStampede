import re
import pandas as pd
from natsort import natsorted
import glob
import os
import sys
import json
# FUNCTION DEFINITION
def getPosition(filename, index):
    """
    This function opens filename,
    and returns position values at 
    position 'index'
    """
    # Check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found")

    df = pd.read_csv(filename).drop_duplicates(subset=['time', 'root_dist'], keep='last')
    df.to_csv(filename, index=False)
    # Check if DataFrame is empty
    if df.empty:
        raise ValueError(f"Dataframe for {filename} is empty")
    
    # Ensure the index is within the bounds of the dataframe
    if index < len(df):
        x_value = df['x'].iloc[index]
        y_value = df['y'].iloc[index]
        z_value = df['z'].iloc[index]
    else:
        raise IndexError(f"Index {index} out of range for dataframe of length {len(df)}")
    
    return x_value, y_value, z_value

def transformPoints(x,y,z):
	"""
	Given the AL center coordinates,
	return the AL sides coordinates. 
    """

	n = len(x)
	if n>1:
		x_new = [0]*(n+1)
		y_new = [0]*(n+1)
		z_new = [0]*(n+1)

		x_new[0] = 1.5*x[0] - 0.5*x[1]
		y_new[0] = 1.5*y[0] - 0.5*y[1]
		z_new[0] = 1.5*z[0] - 0.5*z[1]

		x_new[-1] = 1.5*x[-1] - 0.5*x[-2]
		y_new[-1] = 1.5*y[-1] - 0.5*y[-2]
		z_new[-1] = 1.5*z[-1] - 0.5*z[-2]

		for i in range(1,n):
			x_new[i] = 0.5*x[i-1] + 0.5*x[i]
			y_new[i] = 0.5*y[i-1] + 0.5*y[i]
			z_new[i] = 0.5*z[i-1] + 0.5*z[i]	 	

	else:
		x_new = x
		y_new = y
		z_new = z

	return x_new, y_new, z_new

def getClosestTime(filename, tref):
	"""
	This function opens filename,
    and looks for the time value 
    closest to 'tref' 
    """
	df = pd.read_csv(filename).to_dict()
	t = df.get('time')
	# Get time value closest to ref_t
	index, time_value = min(t.items(), key=lambda x: abs(tref - x[1]))
	return index, time_value;


def getFilenames(regionName, componentName):
	"""
	Search for all the filles
	containing the component name
	"""
	filenames = glob.glob("postProcessing/actuatorLineElements/0/" + regionName + "." + componentName + "*")
        
	# Important to return filenames in sorted order:
	# file0, file1, ... file9, file10, ...
	return natsorted(filenames);


def positionList(regionName, componentName, ref_time):
	""" 
	Loop over all files containing
	component name and get position values
	at t = ref_time
	"""
	x, y, z = [], [], []
	filenames = getFilenames(regionName, componentName)
	index, time = getClosestTime(filenames[1], ref_time)
	
	for filename in filenames:
		xnew, ynew, znew = getPosition(filename, index)
		x.append(xnew)
		y.append(ynew)
		z.append(znew)

	return time, x, y, z;


def createDirectory(path):
	""" 
	If the directory does not exist,
	create it.
	"""
	if not os.path.exists(path):
		os.mkdir(path)

file_counter = 0  # global file counter

def writeVTK(dirName, regionName, time, x, y, z, indexes):
    global file_counter  # access the global counter
    global name
    # Use the file_counter for naming
    vtk_filename = dirName + "/result_{:04d}.vtk".format(file_counter)
    f = open(vtk_filename, "w")
    name = vtk_filename
    headers = ['# vtk DataFile Version 3.0', 'vtk output', 'ASCII', 'DATASET POLYDATA']
    for header in headers:
        f.write(header)
        f.write('\n')

    # Write points
    length = len(x)
    points = 'POINTS ' + str(length) + ' float \n'
    f.write(points)
    for i in range(length):
        px = str(x[i])
        py = str(y[i])
        pz = str(z[i])
        f.write(px + ' ' + py + ' ' + pz + '\n')

    # Write lines
    lines = 'LINES ' + str(length-len(indexes)-1) + ' ' + str(3*(length-len(indexes)-1)) + ' \n'
    f.write(lines)

    # Don't draw lines between different components!
    write = 1    
    for i in range(length-1):
        for num in indexes:
            if(i == num-2):
                write = 0
        if(write):
            f.write('2 ' + str(i+1) + ' ' + str(i+2) + '\n')
        write = 1
    
    f.close()

    file_counter += 1  # increment the counter for next write
    return vtk_filename, name





def readTimes():
	""" Open log.foamListTimes, which includes
		the time folders from OpenFOAM. Then, 
		output these times as a list.
	"""
	f = open("log.foamListTimes", "r")
	times = f.read()
	times_str = times.split("\n")
	f.close()

	del times_str[-1] # Remove last entry (is empty)
	times_float = []
	times_float.append(0) # We also want t=0
	for time in times_str:
		times_float.append(float(time))

	return times_float;
def generate_vtk_series(files_list):
	
	address = "turbine_Geometry/"
	file_name = "AL_timeseries"  # arbitrary

	json_dict = {"file-series-version": "1.0", "files": files_list}
	with open(''.join([address, file_name, ".vtk.series"]), 'w') as f:
		json.dump(json_dict, f)
	
	
def combineList(times,names):
	global files_list
	files_list = []
	
	for time, name in zip(times, names):
   
		file_name = name.split("/")[-1]

    
		file_dict = {"name": file_name, "time": float(time)}

   	 
		files_list.append(file_dict)
	print(files_list)
	return files_list ;
#MAIN CODE
if __name__ == "__main__":
	names = []
	times = [] 
	n = len(sys.argv)
	if n<3:
		print('Not enough arguments passed')
		components = ''
		region = ''
	else:
		region = sys.argv[1]
		components = sys.argv[2:]

	times = readTimes()
	print(times)
	dir_name = region + '_Geometry';
	createDirectory(dir_name)
	for time in times:
		x, y, z, componentIndex = [], [], [], []
		for component in components:
			returned_time, x_center, y_center, z_center = positionList(region, component, time)
			# Get positions of the component
			x_comp, y_comp, z_comp = transformPoints(x_center, y_center, z_center)
			componentIndex.append(len(x_comp))
			# Combine all components in a single list
			for i in range(len(x_comp)):
				x.append(x_comp[i])
				y.append(y_comp[i])
				z.append(z_comp[i])

		# The 'componentIndex' list is used to know, in the appended lists xyz,
		# where each component geometry starts and ends 
		for i in range(1,len(componentIndex)):
			componentIndex[i] = componentIndex[i] + componentIndex[i-1] 
		writeVTK(dir_name, region, time, x, y, z, componentIndex)
		names.append(name)
	names = list(dict.fromkeys(names))
	print(names)
	combineList(times,names)
	generate_vtk_series(files_list)
