#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib

img = nib.load("linmean.nii.gz")

print(img)

data = img.get_fdata()

plt.imshow(data[:,:,20])
plt.show()



#test
#from re import S
#import matplotlib.pyplot
#
#data = (3,6,9,12)
#
#fig, simple_chart= matplotlib.pyplot.subplots()
#
#simple_chart.plot(data)
#matplotlib.pyplot.show()
