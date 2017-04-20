struct mini_constellation {
	int s1;
	int s2;
	double p;
	int last;
};

int mini_mapsize=((3600*(sqrt(DEG_X*DEG_X+DEG_Y*DEG_Y))/ARC_ERR)+1);
int numoldstars=oldstars.size();
int numnewstars=newstars.size();
int mini_numconst=(numoldstars*(numoldstars-1))/2;
int mini_dbsize = mini_mapsize*sizeof(int) + mini_numconst*sizeof(struct mini_constellation);;
int* mini_map = (int*)malloc(mini_dbsize);

memset(mini_map, -1, mini_dbsize);
struct mini_constellation *mini_starptr=(struct mini_constellation*)(&mini_map[mini_mapsize]);

void mini_add_entry(int mini_mapidx,int mini_curr_const) {
	int *staridx;
	for (staridx=&mini_map[mini_mapidx];*staridx!=-1;staridx=&(mini_starptr[*staridx].last));
	if (staridx!=&(mini_starptr[mini_curr_const].last)) *staridx=mini_curr_const;
}

int mmi_l,mmi_m,mmi_h;
int mini_curr_const=0;
for (int i=1;i<numoldstars;i++){
	for (int j=0;j<i;j++){
		mini_starptr[mini_curr_const].s1=j;
		mini_starptr[mini_curr_const].s2=i;
		mini_starptr[mini_curr_const].p=(3600*180.0/PI)*acos(oldstars[i].x*oldstars[j].x+oldstars[i].y*oldstars[j].y+oldstars[i].z*oldstars[j].z);
		mmi_l=(mini_starptr[mini_curr_const].p/ARC_ERR-1)%mini_mapsize;
		mmi_m=(mini_starptr[mini_curr_const].p/ARC_ERR)%mini_mapsize;
		mmi_h=(mini_starptr[mini_curr_const].p/ARC_ERR+1)%mini_mapsize;
		if (mmi_l<0) mmi_l+=mini_mapsize;
		if (mmi_m<0) mmi_m+=mini_mapsize;
		if (mmi_h<0) mmi_h+=mini_mapsize;
		
		mini_add_entry(mmi_l,mini_curr_const);
		mini_add_entry(mmi_m,mini_curr_const);
		mini_add_entry(mmi_h,mini_curr_const);
		mini_curr_const++;
	}
}
int p,mmi;

for (int i=1;i<numnewstars;i++){
	for (int j=0;j<i;j++){
		p=(3600*180.0/PI)*acos(newstars[i].x*newstars[j].x+newstars[i].y*newstars[j].y+newstars[i].z*newstars[j].z);
		mmi=p%mini_mapsize;
		if (mmi<0) mmi+=mini_mapsize;
		for (int staridx=map[mmi];staridx!=-1;staridx=mini_starptr[staridx].last) {
			if (mini_starptr[staridx].p<p+ARC_ERR &&
				mini_starptr[staridx].p>p-ARC_ERR){
				new_s1=stars[a].starnum;
				new_s2=stars[b].starnum;
				old_s1=mini_starptr[staridx].s1;
				old_s2=mini_starptr[staridx].s2;
				//if row 3 column 3 is <0, you got the stars backwards
				weighted_triad(new_s1,new_s2,old_s1,old_s2);
				//uncomment this to allow 180 degree rotation
				//weighted_triad(new_s2,new_s1,old_s2,old_s1);
			}
		}
	}
}

void weighted_triad(new_s1,new_s2,old_s1,old_s2){
	//newstars=A*oldstars
	//S=normalize(newstars[new_s1]);
	//s=normalize(oldstars[old_s1]);
	double wa1,wa2,wa3;
	double wb1,wb2,wb3;
	double va1,va2,va3;
	double vb1,vb2,vb3;
	double weightA,weightB;

	double wc1,wc2,wc3;
	wc1=wa2*wb3 - wa3*wb2;
	wc2=wa3*wb1 - wa1*wb3;
	wc3=wa1*wb2 - wa2*wb1;

	double vc1,vc2,vc3;
	vc1=va2*vb3 - va3*vb2;
	vc2=va3*vb1 - va1*vb3;
	vc3=va1*vb2 - va2*vb1;
	
	double vaXvc1,vaXvc2,vaXvc3;
	double waXwc1,waXwc2,waXwc3;
	double vbXvc1,vbXvc2,vbXvc3;
	double wbXwc1,wbXwc2,wbXwc3;
	
	//cross(va,vc)
	vaXvc1=va3*vc2 - va2*vc3;
	vaXvc2=va1*vc3 - va3*vc1;
	vaXvc3=va2*vc1 - va1*vc2;

	//cross(wa,wc) 
	waXwc1=wa3*wc2 - wa2*wc3;
	waXwc2=wa1*wc3 - wa3*wc1;
	waXwc3=wa2*wc1 - wa1*wc2;

	//(take advantage of (cross(b,a) = -cross(a,b))
	//cross(vb,-vc)
	vbXvc1=vb2*vc3 - vb3*vc2;
	vbXvc2=vb3*vc1 - vb1*vc3;
	vbXvc3=vb1*vc2 - vb2*vc1;

	//cross(wb,-wc) 
	wbXwc1=wb2*wc3 - wb3*wc2;
	wbXwc2=wb3*wc1 - wb1*wc3;
	wbXwc3=wb1*wc2 - wb2*wc1;
	
	double A11;
	double A21;
	double A31,A32,A33;
	
	double B11;
	double B21;
	double B31,B32,B33;
	
	//A=simplify(horzcat(va,vc,vaXvc)*transpose(horzcat(wa,wc,waXwc)))
	A33=(va3*wa3 + vaXvc3*waXwc3 + vc3*wc3)*weightA;
	A32=(va3*wa2 + vaXvc3*waXwc2 + vc3*wc2)*weightA;
	A31=(va3*wa1 + vaXvc3*waXwc1 + vc3*wc1)*weightA;
	A21=(va2*wa1 + vaXvc2*waXwc1 + vc2*wc1)*weightA;
	A11=(va1*wa1 + vaXvc1*waXwc1 + vc1*wc1)*weightA;

	//B=simplify(horzcat(vb,vc,vbXvc)*transpose(horzcat(wb,wc,wbXwc)))
	B33=(vb3*wb3 + vbXvc3*wbXwc3 + vc3*wc3)*weightB;
	B32=(vb3*wb2 + vbXvc3*wbXwc2 + vc3*wc2)*weightB;
	B31=(vb3*wb1 + vbXvc3*wbXwc1 + vc3*wc1)*weightB;
	B21=(vb2*wb1 + vbXvc2*wbXwc1 + vc2*wc1)*weightB;
	B11=(vb1*wb1 + vbXvc1*wbXwc1 + vc1*wc1)*weightB;

	double cz,sz,mz;
	double cy,sy,my;
	double cx,sx,mx;
	
	cz=A11+B11;
	sz=A21+B21;
	mz=sqrt(cz^2+sz^2);
	cz=cz/mz;
	sz=sz/mz;
	
	//flip rotations that are outside of the +/- 90 degree range
	//comment this out for lost in space 
	if (cz<0) {
		cz=-cz;
		sz=-sz;
	}
	cy=sqrt(A32^2+A33^2)+sqrt(B32^2+B33^2);
	sy=-A31-B31;
	my=sqrt(cy^2+sy^2);
	cy=cy/my;
	sy=sy/my;

	cx=A33+B33;
	sx=A32+B32;
	mx=sqrt(cx^2+sx^2);
	cx=cx/mx;
	sx=sx/mx;
	
	double R11,R12,R13;
	double R21,R22,R23;
	double R31,R32,R33;
	
	R11=cy*cz;
	R12=cz*sx*sy - cx*sz;
	R13=sx*sz + cx*cz*sy;
	
	R21=cy*sz;
	R22=cx*cz + sx*sy*sz;
	R23=cx*sy*sz - cz*sx;
	
	R31=-sy;
	R32=cy*sx;
	R33=cx*cy;
}
