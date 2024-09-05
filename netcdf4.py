# import netCDF4
# import numpy as np
# import matplotlib.pyplot as plt

# # Open the NetCDF file
# file_path = 'precip.V1.0.2009.nc'
# dataset = netCDF4.Dataset(file_path, mode='r')

# # Access the precipitation variable
# precipitation = dataset.variables['precip'][:]

# # Select a specific time slice (e.g., the first day)
# time_index = 0  # Change this index to select a different day
# precip_slice = precipitation[time_index, :0, :]

# # Plot the selected time slice
# plt.imshow(precip_slice, cmap='viridis')
# plt.colorbar(label='Precipitation (units)')
# plt.title(f'Precipitation Data on Day {time_index+1}')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.show()

# # Close the dataset
# dataset.close()


from matplotlib import pyplot as plt # import libraries
import pandas as pd # import libraries
import netCDF4 # import libraries
fp='precip.V1.0.2009.nc' # your file name with the eventual path
nc = netCDF4.Dataset(fp) # reading the nc file and creating Dataset
""" in this dataset each component will be 
in the form nt,nz,ny,nx i.e. all the variables will be flipped. """
plt.imshow(nc['precip'][1,:]) 
""" imshow is a 2D plot function
according to what I have said before this will plot the second
iteration of the vertical slize with y = 0, one of the vertical
boundaries of your model. """
plt.show() # this shows the plot
print(nc['precip'][1,:]) # this will print the values of the second iteration of the vertical slize with y = 0