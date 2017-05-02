from getstars import *
import beast
import datetime
from time import time
beast.load_db()

def xyz_points(image_stars_info):
    """
    Converts the (x,y,magnitude) values to x,y,z points
        Input:
            image_stars_info: list of tuples in the form (x,y,magnitude)
        Output:
            star_points: a list of tuples in the form (x,y,z)
    """
    star_points = []
    for pixel_x,pixel_y,mag in image_stars_info:
        #formula for converting from x,y, magnitude to x,y,z
        j=2*np.tan(DEG_X*np.pi/(180*2))*pixel_x/IMG_X #j=(x/z)
        k=2*np.tan(DEG_Y*np.pi/(180*2))*pixel_y/IMG_Y #k=y/z
        x=1./np.sqrt(j*j+k*k+1)
        y=j*x
        z=k*x
        star_points.append([x,y,z])
    return star_points

def group_stars(star_points ,false_stars = MAX_FALSE_STARS):
    if (len(star_points)<4):
        raise NoMatchesFound("Not enough stars")
    if (len(star_points)-4<false_stars):
        false_stars=len(star_points)-4
    star_kd = spatial.cKDTree(star_points)
    #arbitrarily chosen
    #second retval is the star array locations in tree.data
    results = star_kd.query(star_points,false_stars+4)
    return results[1]


def identify_stars(image_stars_info,star_points=[]):
    """
    Takes in a list with star tuples of the form (x,y,mag) and attempts to                                                                                               orm (x,y,mag) and attempts to
    determing the attitude matrix that would transfrom the stars from the image
    to their locations in the database

    Input:
        image_stars_info: list of star tuples of the form (x,y,mag)
        star_points (optional): precomputed x,y,z values of image_stars_info
    Returns:
        matched_stars: database of stars that were matched in the form
    [im_id,db_id,[im_x,im_y,im_z],[db_x,db_y,db_z]]
    Raises:
        NoMatchesFound:
    """

    #give the option to pass in precomputed star points, but dont require it
    if (len(star_points)==0):
        star_points = xyz_points(image_stars_info)

    image_stars_info=np.array(image_stars_info)
    star_ids = []
    try:
        for group in group_stars(star_points):
             query = beast.star_query()
             for i in image_stars_info[group]:
                 query.add_star(i[0],i[1],i[2])
             if (query.search_pilot()):
                 star_ids.append([group[query.im_0],int(query.db_0)])
                 star_ids.append([group[query.im_1],int(query.db_1)])
                 star_ids.append([group[query.im_2],int(query.db_2)])
                 star_ids.append([group[query.im_3],int(query.db_3)])
                 break
    except NoMatchesFound:
        return []
    return [i+star_points[i[0]]+stardb[i[1]][4:7] for i in sort_uniq(star_ids)]

def determine_rotation_matrix(img_path):
    """
    Takes in a pth to an image and determines the attitude of the satellite
    based on the contents of the starfield in the image_stars_info
    Input:
        img_path: absolute path to the image to be evalutated
    Returns:
        a 2D rotation matrix (numpy format) of the image passed in

    """

    img = cv2.imread(img_path)
    image_stars_info = extract_stars(img)
    star_points=xyz_points(image_stars_info)
    sq =identify_stars(image_stars_info,star_points)
    if (len(sq)>0):
        A=np.array([[i[2],i[3],i[4]] for i in sq])
        B=np.array([[i[5],i[6],i[7]] for i in sq])
        R=rigid_transform_3D(A,B)
        #return R

if __name__ == '__main__':
    filterunreliable()
    filterbrightness()
    filterdoublestars()
    while True:
        try:
            img_name=raw_input().rstrip()
        except EOFError:
            break
        if (img_name==''): break
        starttime=time()
        determine_rotation_matrix(img_name)
        print img_name
        print "Time: "+str(time() - starttime)
        sys.stdout.flush()
