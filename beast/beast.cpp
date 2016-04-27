// lower_bound/upper_bound example
#include <iostream>     // cout
#include <fstream>
#include <algorithm>    // lower_bound, upper_bound, sort
#include <vector>       // vector
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace std;
using namespace cv;

struct star {
	double mag;
	double ra;
	double decll;
};

struct starline {
	double dist;
	int s1;
	int s2;
};

struct sort_z {
    bool operator() (Point3f pt1, Point3f pt2) { return (pt1.z > pt2.z);}
};
struct sort_dist {
    bool operator() (starline sl, double sd) { return (sl.dist < sd);}
};

int cat_lines=0;
int dist_lines=0;

vector<star> s;
vector<starline> d;

void initdb() {
	star s_temp;
	fstream cat_f("cat.txt", ios_base::in);
	while(cat_f>>s_temp.mag>>s_temp.ra>>s_temp.decll) {
		s.push_back(s_temp);
		cat_lines++;
	}
	starline d_temp;
	fstream dist_f("dist.txt", ios_base::in);
	while(dist_f>>d_temp.dist>>d_temp.s1>>d_temp.s2) {
		d.push_back(d_temp);
		dist_lines++;
	}
}
Mat src; Mat src_gray;
int thresh = 100;
int max_thresh = 255;


int main (int argc, char** argv) {
	//load the stardb
	initdb();
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
	vector<Point3f> mc(contours.size());
	for( int i = 0; i < contours.size(); i++ ) {
		mu[i] = moments( contours[i], false );
		mc[i] = Point3f(mu[i].m10/mu[i].m00,mu[i].m01/mu[i].m00,mu[i].m00);
	}
	sort(mc.begin(), mc.end(), sort_z());

	vector<vector<int> > star_hits(cat_lines, vector<int>(0) ); //for each star  in our image allocate a vector to keep track of other stars which have matched to it (maybe could increase performance by preallocation)
	double x_diff,y_diff,pt_dist,pt_dist_l,pt_dist_u;
	double ppd=394/9.97;
	int false_positives=0;
	for( int i = 0; i < contours.size(); i++ ) if (mc[i].z>0.0) {
		for( int j = 0; j < i; j++ ) if (mc[j].z>0.0) {
			cout<<mc[i].x<<' '<<mc[i].y<<' '<< mc[i].z<<endl;
			x_diff = mc[i].x - mc[j].x;//
			y_diff = mc[i].y - mc[j].y;
//calculate the distances between all the stars in the image
			pt_dist=sqrt(x_diff*x_diff + y_diff*y_diff);
			pt_dist_l=(pt_dist-0.5)/ppd;
			pt_dist_u=(pt_dist+0.5)/ppd;
			for (vector<starline>::iterator low=lower_bound(d.begin(), d.end(), pt_dist_l,sort_dist());(*low).dist<=pt_dist_u&& low != d.end(); low++){
			//for (int k=0;(*low).dist<=pt_dist_u&&k<low.size(); k++) {//
				star_hits[(*low).s1].push_back((*low).s2);
				star_hits[(*low).s2].push_back((*low).s1);
				if (star_hits[(*low).s1].size()>2&&star_hits[(*low).s2].size()>2) {
					//looks promising, verify that they indeed have two other stars in common before declaring a match
					int verify_count=0;
/*todo: 
1. replace starhits with struct which also stores x,y coordinates of each star in the image (or at least the i and j values)
2. replace star verifier to work off of i and j,
2.5 break star verifier off into its own function
3. preallocate memory for the subvectors in starhits
4. make a mini dist db from the stars in the image
*/

					for (int a=0;a<star_hits[(*low).s1].size();a++) for (int b=0;b<star_hits[(*low).s2].size();b++) if(star_hits[(*low).s1][a]==star_hits[(*low).s2][b]) {
						cout<<star_hits[(*low).s1][a]<<':'<<star_hits[(*low).s2][b]<<endl;
						if(++verify_count==2)  {
							cout <<"match!"<<false_positives<<','<<(*low).s1<<','<<(*low).s2<<endl;
							for (int j=0;j<star_hits[(*low).s1].size();j++) cout<<(*low).s1<<':'<<star_hits[(*low).s1][j]<<endl;
							for (int j=0;j<star_hits[(*low).s2].size();j++) cout<<(*low).s2<<':'<<star_hits[(*low).s2][j]<<endl;
							return 0;
						}
						break;
					}
					false_positives++;
				}
			}
		}
	}
}

