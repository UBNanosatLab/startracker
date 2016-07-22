// lower_bound/upper_bound example
#include <iostream>     // cout
#include <fstream>
#include <algorithm>    // lower_bound, upper_bound, sort
#include <vector>       // vector
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace cv;

struct sort_z {
    bool operator() (Point3f pt1, Point3f pt2) { return (pt1.z > pt2.z);}
};

int cat_lines=0;
int dist_lines=0;

Mat src; Mat src_gray;
int thresh = 150;
int max_thresh = 255;


int main (int argc, char** argv) {
	//extract centroids
	/// Load source image and convert it to gray
	src = imread( argv[1], 1 );
	cvtColor( src, src_gray, CV_BGR2GRAY );
    Mat canny_output;
	vector<vector<Point> > contours;
	vector<Vec4i> hierarchy;

	/// Detect edges using canny
	Canny( src_gray, canny_output, thresh, thresh*2, 3 );
	findContours( canny_output, contours, hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

	/// Get the moments
	vector<Moments> mu(contours.size());
	vector<Point3f> mc;
	for( int i = 0; i < contours.size(); i++ ) {
		mu[i] = moments( contours[i], false );
		if (mu[i].m00>0) mc.push_back(Point3f(mu[i].m10/mu[i].m00,mu[i].m01/mu[i].m00,mu[i].m00));
	}
	sort(mc.begin(), mc.end(), sort_z());
	for (int i = 0;i<mc.size();i++) std::cout <<mc[i].x<<" "<<mc[i].y<<" "<<mc[i].z<<std::endl<<std::flush;
}

