%convert from RA/DEC to rectangular
maxstep=20;
step=maxstep/sqrt(2);
hold on;
decstep=180/floor(180/step);
for dec = -90+decstep/2:decstep:90
	rastep=360/floor(360/(step/cos(deg2rad(dec))));
	ra = [0:rastep:360];	scatter3(cos(deg2rad(ra))*cos(deg2rad(dec)),sin(deg2rad(ra))*cos(deg2rad(dec)),repmat(sin(deg2rad(dec)),numel(ra),1));
end
hold off;
