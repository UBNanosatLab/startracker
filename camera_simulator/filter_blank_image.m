b1=double(imread('b1.png'))/255.0;
b2=double(imread('b2.png'))/255.0;
b3=double(imread('b3.png'))/255.0;
b4=double(imread('b4.png'))/255.0;
b5=double(imread('b5.png'))/255.0;
b6=double(imread('b6.png'))/255.0;
b7=double(imread('b7.png'))/255.0;
b8=double(imread('b8.png'))/255.0;
b9=double(imread('b9.png'))/255.0;
b=(b1.*b2.*b3.*b4.*b5.*b6.*b7.*b8.*b9).^(1/9);
imwrite(b,'blank.png');

