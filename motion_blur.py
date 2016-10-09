
import numpy as np
import cv2
import sys

def blur_edge(img, d=31):
    """
    Blurs the with a gaussian blur in preparation for weiner convolution

    Args:
        img: the image to have its edges blurred
        d: the size of the blur spread

    Returns:
        the blurred image
    """
    h, w  = img.shape[:2]
    img_pad = cv2.copyMakeBorder(img, d, d, d, d, cv2.BORDER_WRAP)
    img_blur = cv2.GaussianBlur(img_pad, (2*d+1, 2*d+1), -1)[d:-d,d:-d]
    y, x = np.indices((h, w))
    dist = np.dstack([x, w-x-1, y, h-y-1]).min(-1)
    w = np.minimum(np.float32(dist)/d, 1.0)
    return img*w + img_blur*(1-w)

def motion_kernel(angle, distance, size=65):
    """
    Produces the matrix (AKA kernel in image processing) used to create the
    desired blur effect.

    Args:
        angle: the angle at which to apply the blur
        distance: amount of spreading that should occur during blurring
        size: width/height of the desired kernel
    Returns:
        the  2D kernel matrix used for the convolution as a numpy array

    """
    kern = np.ones((1, distance), np.float32)
    c, s = np.cos(angle), np.sin(angle)
    A = np.float32([[c, -s, 0], [s, c, 0]])
    size2 = size // 2
    A[:,2] = (size2, size2) - np.dot(A[:,:2], ((distance-1)*0.5, 0))
    kern = cv2.warpAffine(kern, A, (size, size), flags=cv2.INTER_CUBIC)
    print type(kern)
    return kern

def blur(image,angle,length,noise  = 25):
    """
    Blurs the input image to the desired angle and blur spread using Weiner
    Convolution

    Args:
        image: the image to be blurred
        angle: the angle to apply the blur in radians
        length: the spread of the blur on the image
        noise: the signal to noise ratio
    Returns:
        the array of the blurred image

    """
    #only used to display image process
    noise = 10**(-0.1*noise)
    # read fails set img to None
    img = cv2.imread(image, 0)
    if img is None:
        print('Failed to load image:',image)
        sys.exit(1)

    img = np.float32(img)/255.0

    img = blur_edge(img)
    IMG = cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT)


    # performing weiner deconvultion in order to apply a convolution to an
    # un-disturbed image. https://en.wikipedia.org/wiki/Wiener_deconvolution

    ang = np.deg2rad( int(angle))
    distance = int(length)
    psf = motion_kernel(ang, distance)
    psf /= psf.sum()
    psf_pad = np.zeros_like(img)
    #kh,kw = kernel height, kernel width
    kh, kw = psf.shape
    psf_pad[:kh, :kw] = psf
    PSF = cv2.dft(psf_pad, flags=cv2.DFT_COMPLEX_OUTPUT, nonzeroRows = kh)
    PSF2 = (PSF**2).sum(-1)
    iPSF = PSF * (PSF2)[...,np.newaxis]
    RES = cv2.mulSpectrums(IMG, iPSF, 0)
    res = cv2.idft(RES, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT )
    res = np.roll(res, -kh//2, 0)
    res = np.roll(res, -kw//2, 1)

    return res
