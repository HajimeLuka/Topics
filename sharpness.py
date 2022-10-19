#find intensity values of nonlinear images produced at specific coordiantes
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib

#find the intensity values of the image nonlinearmean
data = nib.load("nonlinmean.nii.gz")


img = data.get_fdata()

print(img.size)

nx,ny,nz = img.size
#print(img)

#3 new arrays
Dx = np.zeros((nx,ny,nz))
Dy = np.zeros((nx,ny,nz))
Dz = np.zeros((nx,ny,nz))

#Intensity
#start loop first
img[x,y,z]


#save as nifty image
#must overwrite data, not extract
