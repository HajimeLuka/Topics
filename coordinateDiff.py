import os #need when working with diff directories
import numpy as np
import statistics as stats

#write function that removes outliers from array
def outliers(array, bigArray):
    Array=np.array(bigArray)
    
    q3, q1 = np.percentile(Array, [75 ,25])
    IQR = q3 - q1
    
    low = q1 - (1.5 * IQR)
    high = q3 + (1.5 * IQR)
    
    for i in array:
        if i >= high or i <= low:
            array.remove(i)
            
    return array

#nans have been removed

cwd = os.getcwd()
#/Users/hajimeluka/Desktop/fsl/I3/res/1005print("Current working directory: {0}".format(os.getcwd()))
#define original right and left coordinate arrays
OGright = []
OGleft = []

subjects = [1002, 1003, 1004, 1005, 4000, 4002, 4062, 4068, 4081, 4092, 4105, 4189, 4244, 4458, 4504, 4560, 4598, 4611, 4867, 4889, 5008]

#populate array for original right coordinates
#for loop to go back and forth in directories

for i in subjects:
    os.chdir(str(i))
    file = open("LC_coordR.txt", "r")
    values = file.read().splitlines() #puts the file into an array
#    print(values)
    OGright.append(values)
    file.close()
    os.chdir('..')
#    print(i)
#print("Right: ")
#print(OGright)

#popular array for original left coordinates
for i in subjects:
    os.chdir(str(i))
    file = open("LC_coordL.txt", "r")
    values = file.read().splitlines() #puts the file into an array
#    print(values)
    OGleft.append(values)
    file.close()
    os.chdir('..')
#    print(i)
#print("Left: ")

#print(OGleft)

#define arrays for estimated LC location
Eright = []
Eleft = []

#change directories into res
os.chdir('res')

#populate estimated right
for i in subjects:
    os.chdir(str(i))
    file = open("LCCoordR.txt", "r")
    values = file.read().splitlines() #puts the file into an array
#    print(values)
    Eright.append(values)
    file.close()
    os.chdir('..')
#    print(i)
#print("Estimated Right: ")
#print(Eright)

#populate estimated left
for i in subjects:
    os.chdir(str(i))
    file = open("LCCoordL.txt", "r")
    values = file.read().splitlines() #puts the file into an array
#    print(values)
    Eleft.append(values)
    file.close()
    os.chdir('..')
#    print(i)
#print("Estimated Left: ")
#print(Eleft)




###find absolute differences
#tempRight1 = np.char.split(OGright)
#tempRight2 = np.char.split(Eright)

#OG right temp
tempRight1=[]
#E right temp
tempRight2=[]
temp = " "

for i in OGright:
    temp = temp.join(i)
#    print(temp)
    x = temp.split()
    tempRight1.append(x)
    temp = " "

        
for i in Eright:
    temp = temp.join(i)
#    print(temp)
    x = temp.split()
    tempRight2.append(x)
    temp = " "
    

#
#print("OG: ")
#
#print(tempRight1)
#
#print("E: ")
#
#print(tempRight2)
#
#
#print(tempRight1[0][1])
#


#test = int(tempRight1[0][0]) - int(tempRight1[0][1])
#
#print(test)
#
#
intArrayR1=[]
intArrayR2=[]
#
##intArrayR1 = [int(i) for i in tempRight1]

for i in tempRight1:
    temp=temp.join(i)
    x = temp.split()
    for j in range(0,3):
#        print(x[j])
        intArrayR1.append(float(x[j]))
    temp = " "
    
#print(intArrayR1)

for i in tempRight2:
    temp=temp.join(i)
    x = temp.split()
    for j in range(0,3):
#        print(x[j])
        intArrayR2.append(float(x[j]))
    temp = " "
    
#print(intArrayR2)

diff = []

intArrayR1=np.array(intArrayR1)
intArrayR2=np.array(intArrayR2)

intArrayR1=np.round(intArrayR1, 2)
intArrayR2=np.round(intArrayR2, 2)

#TAKE OUT ABS
diff = abs(np.subtract(intArrayR1, intArrayR2))

diff = np.round(diff, 2)

#cleaned difference array (1dp)
difference=[]

for i in diff:
#    print(i)
    difference.append(i)
    
#print(difference)

#take average diff for x,y and z
count=0
county=-100;
countz=-100;
Xr = []
Yr = []
Zr = []
#store x difference values into array
for i in difference:
    if count==0 or count%3==0:
        Xr.append(i)
    if count==1:
        county=0
    if county%3==0 and county >= 0:
        Yr.append(i)
    if count==2:
        countz=0
    if countz%3==0 and countz >= 0:
        Zr.append(i)
        
    county=county+1
    count=count+1
    countz=countz+1
    
#print(Xr)
#print(Yr)
#print(Zr)


#DO THE SAME FOR THE LEFT LC

#OG right temp
tempLeft1=[]
#E right temp
tempLeft2=[]
temp = " "

for i in OGleft:
    temp = temp.join(i)
#    print(temp)
    x = temp.split()
    tempLeft1.append(x)
    temp = " "

        
for i in Eleft:
    temp = temp.join(i)
#    print(temp)
    x = temp.split()
    tempLeft2.append(x)
    temp = " "
    
    

#
#
intArrayL1=[]
intArrayL2=[]


for i in tempLeft1:
    temp=temp.join(i)
    x = temp.split()
    for j in range(0,3):
#        print(x[j])
        intArrayL1.append(float(x[j]))
    temp = " "
    
#print(intArrayR1)

for i in tempLeft2:
    temp=temp.join(i)
    x = temp.split()
    for j in range(0,3):
#        print(x[j])
        intArrayL2.append(float(x[j]))
    temp = " "
    
#print(intArrayR2)

diffL = []

intArrayL1=np.array(intArrayL1)
intArrayL2=np.array(intArrayL2)

intArrayL1=np.round(intArrayL1, 2)
intArrayL2=np.round(intArrayL2, 2)

diffL = abs(np.subtract(intArrayL1, intArrayL2))

diffL = np.round(diffL, 2)

#cleaned difference array (1dp)
differenceL=[]

for i in diffL:
#    print(i)
    differenceL.append(i)
    
#print(difference)

#take average diff for x,y and z
count=0
county=-100;
countz=-100;
Xl = []
Yl = []
Zl = []
#store x difference values into array
for i in differenceL:
    if count==0 or count%3==0:
        Xl.append(i)
    if count==1:
        county=0
    if county%3==0 and county >= 0:
        Yl.append(i)
    if count==2:
        countz=0
    if countz%3==0 and countz >= 0:
        Zl.append(i)
        
    county=county+1
    count=count+1
    countz=countz+1
    
#print(Xl)
#print(Yl)
#print(Zl)

#remove outliers
Xr = outliers(Xr, difference)
Yr = outliers(Yr, difference)
Zr = outliers(Zr, difference)
Xl = outliers(Xl, differenceL)
Yl = outliers(Yl, differenceL)
Zl = outliers(Zl, differenceL)

    
#print(Xr)
#print(Yr)
#print(Zr)
#
#print(Xl)
#print(Yl)
#print(Zl)

#find mean of differences and graph
rightmeanx = stats.mean(Xr)
rightmeany = stats.mean(Yr)
rightmeanz = stats.mean(Zr)

leftmeanx = stats.mean(Xl)
leftmeany = stats.mean(Yl)
leftmeanz = stats.mean(Zl)

resR = [rightmeanx, rightmeany, rightmeanz]
resL = [leftmeanx, leftmeany, leftmeanz]

print(resR, resL)


