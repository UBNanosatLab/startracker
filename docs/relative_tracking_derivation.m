clear
syms x x0 x1 x2 x3 y y0 y1 y2 y3 m0 m1 m2 m3 w a0 a1
I0=m0*exp(-(x-x0)^2) + m1*exp(-(x-x1)^2)
I1=m2*exp(-(x-x2)^2) + m3*exp(-(x-x3)^2)
corr=ifourier(-fourier(I0,x,w)*ifourier(I1,x,w),w,x)

-(pi*m0*m2*fourier(combine(exp(- w^2/4 - x0*w*1i)*exp(- w^2/4 + x2*w*1i),'exp'), w, -x) + pi*m0*m3*fourier(combine(exp(- w^2/4 - x0*w*1i)*exp(- w^2/4 + x3*w*1i),'exp'), w, -x) + pi*m1*m2*fourier(combine(exp(- w^2/4 - x1*w*1i)*exp(- w^2/4 + x2*w*1i),'exp'), w, -x) + pi*m1*m3*fourier(combine(exp(- w^2/4 - x1*w*1i)*exp(- w^2/4 + x3*w*1i),'exp'), w, -x))
/(4*pi^2)


- m0*m2*diff(exp(-(x - x0 + x2)^2/2),x) - m0*m3*diff(exp(-(x - x0 + x3)^2/2),x) - m1*m2*diff(exp(-(x - x1 + x2)^2/2),x) - m1*m3*diff(exp(-(x - x1 + x3)^2/2),x)
/(8*pi)^(1/2)



%remove cross stars
solve(m0*m2*exp(-(x - x0 + x2)^2/2)*(x - x0 + x2) + m1*m3*exp(-(x - x1 + x3)^2/2)*(x - x1 + x3)==0,x)


%aproximate around exp(0), and add scaling constant ai (real equation is exp(-ai(x-x1)))

solve(m0*m2*(x - x0 + x2)*a0 + m1*m3*(x - x1 + x3)*a1==0,x)

x=(a0*m0*m2*(x0 - x2) + a1*m1*m3*(x1 - x3))/(a0*m0*m2 + a1*m1*m3)


%part 2 - weighted TRIAD
%TRIAD method takes two observations of two vectors, and calculates the rotation matrix between them
%the rotation matrix perfors the following steps:

%1. line up the first vector image  with the first vector of image 2
%2. rotate the second vector of image 1 about the first vector untill it falls 
%in the line made by the first vector and the second vector of image 2
% The result is that vector one is perfectly aligned, while vector 2 is aligned as well as it can be
%given the constraint theat vector 1 be perfectly aligned

%For better control, one can swap vectors one and two and calculate a second rotation matrix.
%you can then split these up into individual rotation matrices for each axis,
%and interpolate between them according to a set of weights.
%in our case, we would like to use the weights which optimize correlation between the
%stars in image one and image two

%derivation:
clear
syms wa1 wa2 wa3 wb1 wb2 wb3 va1 va2 va3 vb1 vb2 vb3
assume([wa1 wa2 wa3 wb1 wb2 wb3 va1 va2 va3 vb1 vb2 vb3],'real')
wa=[wa1;wa2;wa3]
wb=[wb1;wb2;wb3]
va=[va1;va2;va3]
vb=[vb1;vb2;vb3]
syms vc1 vc2 vc3 wc1 wc2 wc3 vaXvc1 vaXvc2 vaXvc3 waXwc1 waXwc2 waXwc3
assume([vc1 vc2 vc3 wc1 wc2 wc3 vaXvc1 vaXvc2 vaXvc3 waXwc1 waXwc2 waXwc3],'real')
wc=cross(wa,wb)
wc=wc/norm(wc)
vc=cross(va,vb)
vc=vc/norm(vc)
%wc=[wc1;wc2;wc3]
%vc=[vc1;vc2;vc3]
vaXvc=cross(va,vc)
waXwc=cross(wa,wc)
%vaXvc=[vaXvc1;vaXvc2;vaXvc3]
%waXwc=[waXwc1;waXwc2;waXwc3]
A=simplify(horzcat(va,vc,vaXvc)*transpose(horzcat(wa,wc,waXwc)))

%[s1old s2old s1new s2new]

clear
IMG_X=640
IMG_Y=480
DEG_X=36.99
DEG_Y=28.06
px=[0.0 100.0 50.0 152.0]
py=[100.0 200.0 100.0 200.0]

j=2*tan(DEG_X*pi/(180*2))*px/IMG_X;
k=2*tan(DEG_Y*pi/(180*2))*py/IMG_Y;
x=1./sqrt(j.*j+k.*k+1);
y=j.*x;
z=k.*x;
wa=[x(1);y(1);z(1)]%r1
wb=[x(2);y(2);z(2)]%r2
va=[x(3);y(3);z(3)]%R1
vb=[x(4);y(4);z(4)]%R2
wc=cross(wa,wb)
wc=wc/norm(wc)
vc=cross(va,vb)
vc=vc/norm(vc)
vaXvc=cross(va,vc)
waXwc=cross(wa,wc)
A=horzcat(va,vc,vaXvc)*transpose(horzcat(wa,wc,waXwc))
[x;y;z] 
A*[x;y;z] 


%va=[va1;va2;va3]
%vb=[vb1;vb2;vb3]
%syms vc1 vc2 vc3 wc1 wc2 wc3 vbXvc1 vbXvc2 vbXvc3 wbXwc1 wbXwc2 wbXwc3
%assume([vc1 vc2 vc3 wc1 wc2 wc3 vbXvc1 vbXvc2 vbXvc3 wbXwc1 wbXwc2 wbXwc3],'real')
%wc=-wc
%vc=-vc
%vbXvc=[vbXvc1;vbXvc2;vbXvc3]
%wbXwc=[wbXwc1;wbXwc2;wbXwc3]
%B=simplify(horzcat(vb,vc,vbXvc)*transpose(horzcat(wb,wc,wbXwc)))

%we split up the rotation matrices and make use of small angle approximate interpolation
%in order to avoid the use of trigonometric functions and speed up computation
%derivation:
%see http://nghiaho.com/?page_id=846

%syms cx sx cy sy cz sz
%assume([cx sx cy sy cz sz],'real')
%cx=simplify(cos(atan2(A32,A33)))
%sx=simplify(sin(atan2(A32,A33)))
%
%X=[[1 0 0]
%[0 cx -sx]
%[0 sx cx]]
%
%%cy=simplify(cos(atan2(-A31,sqrt(A33^2+A32^2))))
%%sy=simplify(sin(atan2(-A31,sqrt(A33^2+A32^2))))
%
%Y=[[cy 0 sy]
%[0 1 0]
%[-sy 0 cy]]
%
%cz=simplify(cos(atan2(A21,A11)))
%sz=simplify(sin(atan2(A21,A11)))
%
%Z=[[cz -sz 0]
%[sz cz 0]
%[0 0 1]]


clear
syms wa1 wa2 wa3 wb1 wb2 wb3 va1 va2 va3 vb1 vb2 vb3 weightA weightB
assume([wa1 wa2 wa3 wb1 wb2 wb3 va1 va2 va3 vb1 vb2 vb3 weightA weightB],'real')


wc1=wa2*wb3 - wa3*wb2
wc2=wa3*wb1 - wa1*wb3
wc3=wa1*wb2 - wa2*wb1

vc1=va2*vb3 - va3*vb2
vc2=va3*vb1 - va1*vb3
vc3=va1*vb2 - va2*vb1

%cross(va,vc)
vaXvc1=va3*vc2 - va2*vc3
vaXvc2=va1*vc3 - va3*vc1
vaXvc3=va2*vc1 - va1*vc2

%cross(wa,wc) 
waXwc1=wa3*wc2 - wa2*wc3
waXwc2=wa1*wc3 - wa3*wc1
waXwc3=wa2*wc1 - wa1*wc2


%(take advantage of (cross(b,a) = -cross(a,b))
%cross(vb,-vc)
vbXvc1=vb2*vc3 - vb3*vc2
vbXvc2=vb3*vc1 - vb1*vc3
vbXvc3=vb1*vc2 - vb2*vc1

%cross(wb,-wc) 
wbXwc1=wb2*wc3 - wb3*wc2
wbXwc2=wb3*wc1 - wb1*wc3
wbXwc3=wb1*wc2 - wb2*wc1

%A=simplify(horzcat(va,vc,vaXvc)*transpose(horzcat(wa,wc,waXwc)))
A33=(va3*wa3 + vaXvc3*waXwc3 + vc3*wc3)*weightA
A32=(va3*wa2 + vaXvc3*waXwc2 + vc3*wc2)*weightA
A31=(va3*wa1 + vaXvc3*waXwc1 + vc3*wc1)*weightA
A21=(va2*wa1 + vaXvc2*waXwc1 + vc2*wc1)*weightA
A11=(va1*wa1 + vaXvc1*waXwc1 + vc1*wc1)*weightA

%B=simplify(horzcat(vb,vc,vbXvc)*transpose(horzcat(wb,wc,wbXwc)))
B33=(vb3*wb3 + vbXvc3*wbXwc3 + vc3*wc3)*weightB
B32=(vb3*wb2 + vbXvc3*wbXwc2 + vc3*wc2)*weightB
B31=(vb3*wb1 + vbXvc3*wbXwc1 + vc3*wc1)*weightB
B21=(vb2*wb1 + vbXvc2*wbXwc1 + vc2*wc1)*weightB
B11=(vb1*wb1 + vbXvc1*wbXwc1 + vc1*wc1)*weightB

cz=A11+B11
sz=A21+B21
mz=sqrt(cz^2+sz^2)
cz=cz/mz
sz=sz/mz
%disallow 180 degree rotations
%if cz<0
%	cz=-cz
%	sz=-sz
%end

%Todo check if x,y,z need to be renamed

cy=sqrt(A32^2+A33^2)+sqrt(B32^2+B33^2)
sy=-A31-B31
my=sqrt(cy^2+sy^2)
cy=cy/my
sy=sy/my

cx=A33+B33
sx=A32+B32
mx=sqrt(cx^2+sx^2)
cx=cx/mx
sx=sx/mx

R=[[ cy*cz, cz*sx*sy - cx*sz, sx*sz + cx*cz*sy]
[ cy*sz, cx*cz + sx*sy*sz, cx*sy*sz - cz*sx]
[   -sy,            cy*sx,            cx*cy]]
