import sys
import numpy as np
from math import sqrt
from getstars import extract_stars
import _beast
from scipy.spatial import kdtree
#adds the path to gendby.py for use as simple import
sys.path.insert(0, '../catalog_gen/')
from os import chdir
#changes directory so that gendb.py can load the files it needs to work
chdir("../catalog_gen")
import gendb
execfile("calibration/calibration.txt")


def rigid_transform_3D(A, B):
    """
    Takes in two matrices of points and finds the attitude matrix needed to
    transform one onto the other

    Input:
        A: nx3 matrix
        B: nx3 matrix
        Note: the "n" dimension of both matrices must match
    Output:
        attitude_matrix: returned as a numpy matrix
    """
    assert len(A) == len(B)

    N = A.shape[0]; # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # center the points
    AA = A - np.tile(centroid_A, (N, 1))
    BB = B - np.tile(centroid_B, (N, 1))

    # dot is matrix multiplication for array
    H = np.transpose(AA) * BB

    U, S, Vt = np.linalg.svd(H)

    attitude_matrix = Vt.T * U.T

    # special reflection case
    if np.linalg.det(attitude_matrix) < 0:

       Vt[2,:] *= -1
       attitude_matrix = Vt.T * U.T

    return attitude_matrix

def determine_attitude(image_stars_info):
    """
    Takes in a list with star tuples of the form (x,y,mag) and attempts to
    determing the attitude matrix that would transfrom the stars from the image
    to their locations in the database

    Input:
        image_stars_info: llist of star tuples of the form (x,y,mag)
        Note: it is recommended that you directly pass the return value from
        getstars.py as the input to this function
    Returns:
        attitude_matrix: returned as a numpy matrix
        matched_stars: database ids of the stars that were matched
    """
    chdir("../catalog_gen")
    stardb = gendb.getstardb()
    #back to original dir to load image


    star_points = []

    # used to map (x,y,z) of star to magnitude for quick lookup when the KDTree
    # returns neighbors. The tree only returns the (x,y,z) and we need the magnitude
    # to query beast
    mag_lookup = {}

    for pixel_x,pixel_y,mag in image_stars_info:

        #formula for converting from x,y, magnitude to x,y,z
        j=2*np.tan(DEG_X*np.pi/(180*2))*pixel_x/IMG_X #j=(x/z)
        k=2*np.tan(DEG_Y*np.pi/(180*2))*pixel_y/IMG_Y #k=y/z
        x=1./np.sqrt(j*j+k*k+1)
        y=j*x
        z=k*x
        star_points.append([x,y,z])
        mag_lookup[(x,y,z)] = (pixel_x,pixel_y,mag)

    star_kd = kdtree.KDTree(star_points)
    #arbitrarily chosen
    false_stars = 7
    #second retval is the star array locations in tree.data
    results = star_kd.query(star_points,false_stars+3)
    query_groups = []
    #TODO:fix the perform_search call to use x,y,z,mag instead of passing
    # the x,y,mag and having beast perform the conversion that we already performed
    for neighbors in results[1]:
        group = []
        for star in neighbors:
            coords = star_kd.data[star]
            group.append(list(mag_lookup[tuple(coords)]))

        query_groups.append(group)
    found_constellation = []
    for group in query_groups:
         results = _beast.perform_search(group)
         if results[0]>=0:
             results = [int(x) for x in results]
             star_to_data = {}
             for i in range(0,len(results),2):
                 star_to_data[results[i]] = stardb[results[i+1]]
             x=[]
             y=[]
             z=[]
             for i in star_to_data:
                 x.append(group[i][0])
                 y.append(group[i][1])
                 z.append(group[i][2])
             pic_xyz = np.matrix([x,y,z])
             x2=[]
             y2=[]
             z2=[]

             for i in star_to_data:
                x2.append(star_to_data[i][4])
                y2.append(star_to_data[i][5])
                z2.append(star_to_data[i][6])
             actual_xyz = np.matrix([x2,y2,z2])

             matched_stars=[]
             for i in range(1,len(results),2):
                 matched_stars.append(results[i])

             return rigid_transform_3D(pic_xyz,actual_xyz),matched_stars
chdir("../beast")
image_stars_info = extract_stars("polaris-1s-gain38-4.bmp")
print determine_attitude(image_stars_info)
