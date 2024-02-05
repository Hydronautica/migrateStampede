#!/bin/bash

PFAD=log.overWaveDyMFoam
EXCL=10
N=3 # Number of corrector steps

# Create data directory
mkdir -p data

# Extract the last 'Centre of mass' for each time step after the N-th PIMPLE iteration
awk -v N="$N" '
/Time =/ {
  # Skip lines that do not represent the start of a new time step
  if (! /Loop no./) {
    if (count == N && last_time != "") {
      print last_time, last_x, last_y, last_z;
    }
    # Extract the numerical time value
    split($3, timeParts, " ");
    time = timeParts[1];
    count = 0;
  }
}
/Centre of mass:/ {
  if (time != "" && count < N) {
    count++;
    if (count == N) {
      # Remove the parentheses and store the values
      gsub(/\(|\)/, "", $0);
      last_time = time;
      last_x = $(NF-2);
      last_y = $(NF-1);
      last_z = $NF;
    }
  }
}
END {
  if (count == N && last_time != "") {
    print last_time, last_x, last_y, last_z;
  }
}
' OFS=',' "$PFAD" > data/centreOfMassTemp.dat

# Add header and remove last EXCL lines
echo "#Time, x, y, z" > data/centreOfMass.dat
tail -n +2 data/centreOfMassTemp.dat | head -n -$EXCL >> data/centreOfMass.dat

# Clean up temporary files
rm -f data/centreOfMassTemp.dat

