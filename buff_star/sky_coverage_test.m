%convert from RA/DEC to rectangular
clear
maxstep=2.76;
step=maxstep/sqrt(2);
decstep=180/floor(180/step);
B=[];
for dec = -90+decstep/2:decstep:90
	rastep=360/floor(360/(step/cos(deg2rad(dec))));
	ra = [0:rastep:360];
	B=vertcat(B,horzcat(cos(deg2rad(ra))'*cos(deg2rad(dec)),sin(deg2rad(ra))'*cos(deg2rad(dec)),repmat(sin(deg2rad(dec)),numel(ra),1)));
end
%hold on;
%scatter3(B);
%hold off;

load Stars.mat;
A=horzcat(Star(1,:).Vector);

%temp=csvread('catalog.dat');
%A=horzcat(cos(deg2rad(temp(:,3))).*cos(deg2rad(temp(:,4))),sin(deg2rad(temp(:,3))).*cos(deg2rad(temp(:,4))),sin(deg2rad(temp(:,4))))';

C=sum(acos(B*A)<deg2rad(maxstep),2);
for index = 1:10
	D(index)=sum(C>=index)/numel(C);
end
plot(D);
