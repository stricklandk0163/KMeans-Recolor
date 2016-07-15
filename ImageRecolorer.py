from PIL import Image
import math
import random

#RGB color with division, addition, equality, manhattan distance, and string casting functions
class Color:
    #RGB values for color group
    r = 0
    g = 0
    b = 0

    #Initialize new color group with r, g, and b values
    def __init__(self, r, g, b):

        self.r = r
        self.g = g
        self.b = b

    #Find the manhattan distance to the color in 3 dimensions r,g, and b
    def dist(self, other):
        return abs(self.r - other.r) + abs(self.g - other.g) + abs(self.b - other.b)

    #Cast as string for printing
    def __str__(self):
        return "("+str(self.r)+","+str(self.g)+","+str(self.b)+")"

    #Check if two colors are equal (rgb)
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    #Add two colors together
    def __iadd__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)

    #Divide the count by some constant (denominator)
    def __itruediv__(self, denominator):
        return Color(math.floor(round(self.r/denominator, 0)), math.floor(round(self.g/denominator,0)), math.floor(round(self.b/denominator,0)))

#Passed list of weights
#Chooses a random index from list with the probability of the weight at that index
def randomWeightedIndex(weights):
    totals = []
    sumtotal = 0

    for weight in weights:
        sumtotal += weight
        totals.append(sumtotal)

    rand = random.random() * sumtotal
    for i, total in enumerate(totals):
        if rand < total:
            return i

#Passed k (number of centers to be chosen) and imgcolors (set of image colors to choose centers from)
#Generate k center colors to serve as the initial starting points in the kmeans algorithm
def generateCenters(k, imgcolors):
    #Choose random starting point
    random.seed(4)
    randIndex = random.randrange(k)
    centers = [imgcolors[randIndex]]

    #Using kmeans++ algorithm calculate initial centers 2...k
    for i in range(1, k):

        #The weight of each point in kmeans++ equals the distance to the nearest previously chosen center
        distances = []
        for color in imgcolors:
            closestCenterDist = float('inf')
            for center in centers:
                centerDist = color.dist(center)
                if centerDist < closestCenterDist:
                    closestCenterDist = centerDist
            distances.append(closestCenterDist)

        #Calculate the index of the color to be chosen as a center
        i = randomWeightedIndex(distances)
        centers.append(imgcolors[i])
    return centers

#Passed k (number of centers to be chosen),
      # imgcolors (set of image colors to choose centers from)
      # maxIteration (number of iterations to run before quiting)
#Calculate the kmeans classes to use to classify colors in image
def findKMeansClasses(k, imgcolors, maxIteration):
    #Generate k starting centers to run kmeans on
    centerColors = generateCenters(k, imgcolors)

    iteration=0
    prevCenterColors = []

    #create 2d array of clusters with each cluser's index aligning with a corresponding center in the center colorColors array
    clusters = []
    for i in range(k):
        clusters.append([])

    #Todo may be worthwhile to open multiple threads to accomplish these computations (Big bottleneck)
    #Run kmeans algorithm to calculate classes
    while (prevCenterColors != centerColors) and iteration < maxIteration:
        #Loop through colors and append each color to the cluster with the nearest matching center
        for color in imgcolors:
            closestCenterIndex = 0
            closestCenterDist = float("inf")
            index = 0
            for centerColor in centerColors:
                distToCenterColor = color.dist(centerColor)
                if distToCenterColor < closestCenterDist:
                    closestCenterDist = distToCenterColor
                    closestCenterIndex = index
                clusters[closestCenterIndex].append(color)
                index += 1

        prevCenterColors = centerColors

        #Compute the average of each cluster and overwrite each center with the newly computed center value
        centerColors = []
        for cluster in clusters:
            if len(cluster) > 0:
                averageClusterColor = Color(0, 0, 0)
                for color in cluster:
                    averageClusterColor += color
                averageClusterColor /= len(cluster)
                centerColors.append(averageClusterColor)

        iteration += 1
        print(iteration)
    return centerColors

if __name__ == "__main__":
    #Todo variables could be passed from commandline instead
    img = Image.open('input.jpg' )
    k = 20
    maxIterations = 15

    #Count the pixels into color groups
    pix = img.load()
    rgbcols = []
    #Loop for every 100th pixel in image (pixels have x,y coords)
    #Todo different sized images should be spliced differently as smaller images take less computation
    for x in range(img.size[0])[::10]:
        for y in range(img.size[1])[::10]:
            curpix = pix[x,y]
            rgbcols.append(Color(curpix[0], curpix[1], curpix[2]))

    #Find k classes to be used to classify each rgb color in the image
    classes = findKMeansClasses(k, rgbcols, maxIterations)

    #Loop through each pixel in the passed image
    #Todo may be worthwhile to open multiple threads to accomplish these computations (Big bottleneck)
    im2 = Image.new(img.mode, img.size)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            closestCenterIndex = 0
            closestCenterDist = float("inf")
            index = 0
            #Classify the pixel into one of the classes computed by kmeans++
            for curclass in classes:
                curpix = pix[x,y]
                curPixColor=Color(curpix[0],curpix[1],curpix[2])
                distToCenterColor=curPixColor.dist(curclass)
                if distToCenterColor < closestCenterDist:
                    closestCenterDist = distToCenterColor
                    closestCenterIndex = index
                index+=1

                #Write to im2 with the rgb value of the nearest kmeans class
                im2.putpixel((x,y), (classes[closestCenterIndex].r, classes[closestCenterIndex].g, classes[closestCenterIndex].b))
    im2.save("output.png")














