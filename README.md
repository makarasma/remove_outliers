# remove_outliers
A Python script that removes outlier data points using DBSCAN algorithm.

Use -f (--file) flag to select an input file with the data.

This may be useful when dealing with a lot of features and manual removal is too tedious.
This script was used as a part of my workflow in the master's thesis project where outliers were removed from medical data. 
The script is tailored to the data I was handling in my master's thesis project and may not generalize well to other data formats.

The script assumes that a first row in the input file is a header with feature names.
The script assumes that every row in the input file represents an observation and every column represents a feature.
The script skips the first column which is reserved for an ID of the observation.
Only continiuous data is scanned for outliers. Categorical data is skipped.

The initial file is backed-up and the new file takes the original file name.
An output folder is produced with .log file and .png visuals that show data points and outliers.

