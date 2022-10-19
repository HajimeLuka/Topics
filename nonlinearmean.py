from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib

img = nib.load("nonlinmean.nii.gz")

print(img)

data = img.get_fdata()

plt.imshow(data[:,:,20])
plt.show()

