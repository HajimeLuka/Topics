import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#Iteration 3 - plotting difference using scatter plot

xr = [4.9, 0.71, 1.34, 0.41, 0.43, 0.13, 1.41, 0.32, 0.79, 0.74, 1.5, 1.69, 0.06, 1.69, 1.91, 1.16, 1.98]
yr = [3.44, 4.6, 2.98, 1.95, 0.36, 1.67, 1.0, 0.86, 0.26, 0.34, 0.54, 0.09, 0.57, 0.74, 0.42, 0.7, 0.38]

plt.title("Test")
plt.xlabel("difference in X")
plt.ylabel("difference in Y")
plt.scatter(xr, yr)
plt.show()

