#!/bin/bash

PFAD=log.overWaveDyMFoam
EXCL=10
N=3 # Number of corrector steps

# Create data directory
mkdir -p data

# Extract the last 'Orientation' for each time step after the N-th PIMPLE iteration
awk -v N="$N" '
/Time =/ {
  if (! /Loop no./) {
    if (count == N && last_time != "") {
      print last_time, last_orient;
    }
    # Extract the numerical time value
    split($3, timeParts, " ");
    time = timeParts[1];
    count = 0;
  }
}
/Orientation:/ {
  if (time != "" && count < N) {
    count++;
    if (count == N) {
      # Remove the parentheses and store the orientation vector
      gsub(/\(|\)/, "", $0);
      last_time = time;
      last_orient = $(NF-8) " " $(NF-7) " " $(NF-6) " " $(NF-5) " " $(NF-4) " " $(NF-3) " " $(NF-2) " " $(NF-1) " " $NF;
    }
  }
}
END {
  if (count == N && last_time != "") {
    print last_time, last_orient;
  }
}
' OFS=',' "$PFAD" > data/orientationTemp.dat

# Add header and remove last EXCL lines
echo "#Time, Orientation" > data/orientation.dat
tail -n +2 data/orientationTemp.dat | head -n -$EXCL >> data/orientation.dat

# Clean up temporary files
rm -f data/orientationTemp.dat

