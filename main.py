#!/usr/bin/env python

'''
    Based on demo_freenect.py from the https://github.com/amiller/libfreenect-goodies.git
'''

import cv
import numpy as np
import random
import time
from PIL import Image
from NoFilter import NoFilter
from BackgroundFilter import BackgroundFilter
from RectsFilter import RectsFilter
from DiscoFilter import DiscoFilter
from OverlayFilter import OverlayFilter
import imgtools


class Kinector(object):
    """ Does awesome stuff with the Kinect. """
    def __init__(self, kinect, filters=[], dummymode=False, buffersize=3, showoverlay=False, record=False, canny=False, hough=False):
        self.running = False
        self.kinect = kinect
        self.smoothBuffer = imgtools.SmoothBuffer(buffersize)
        self.dummymode = dummymode
        self.showoverlay = showoverlay
        self.threshold = np.empty(shape=(480, 640, 3)).fill(50)
        self.balldetector = imgtools.BallDetector([180, 30, 30], threshold=100)
        self.record = record
        self.canny = canny
        self.hough = hough


        self.filters = []

        if 'swapbackground' in filters:
            self.filters.append(BackgroundFilter('bg.jpg'))

        if 'disco' in filters:
            self.filters.append(DiscoFilter())

        if 'detectball' in filters:
            self.filters.append(RectsFilter())

        self.filters.append(NoFilter())

        if 'overlay' in filters:
            self.filters.append(OverlayFilter())

    def loop(self):
        """ Start the loop which is terminated by hitting a random key. """
        self.running = True
        while self.running:
            if self.record:
                self.kinect.snapshot()
            else:
                self._step()
            key = cv.WaitKey(5)
            self.running = key in (-1, 32)
            if key == 32: # space bar
                self.kinect.snapshot()

    def _step(self):
        """ One step of the loop, do not call on its own. Please. """
        # Get a fresh frame
        (rgb, depth) = self.kinect.get_frame()

        # reduce depth from 2048 to 256 values
        depth = depth / 8

        args = {}
        args['color'] = rgb[240, 320]

        for filter in self.filters:
            rgb, depth = filter.filter(rgb, depth, args)

        rgb_opencv = cv.fromarray(np.array(rgb[:,:,::-1]))
        cv.ShowImage('display', rgb_opencv)

        return


        # Normalize depth values to be 0..255 instead of 0..2047
        # depth = depth / 8

        # self.smoothBuffer.add(depth)
        # depth = self.smoothBuffer.get()

        if self.canny:
            depth_opencv = imgtools.canny(depth, as_cv=True)
        else:
            depth_opencv = cv.fromarray(np.array(depth[:,:], dtype=np.uint8))

        if self.hough:
            rgb = imgtools.hough(rgb, depth)

        # show holes
        #depth = self.balldetector.detectHoles(depth)
        depth = depth / 8
        rgb_opencv = cv.fromarray(np.array(rgb[:,:,::-1]))
        depth_opencv = cv.fromarray(np.array(depth[:,:], dtype=np.uint8))
        depth_opencv_tmp = cv.fromarray(np.array(depth[:,:], dtype=np.uint8))
        self.balldetector.drawRects(rgb_opencv, depth_opencv_tmp, depth_opencv)
        depth_opencv = cv.fromarray(np.array(depth[:,:], dtype=np.uint8))
        depth_opencv = depth_opencv_tmp

        # rgb_opencv = imgtools.maxima(rgb, depth)

        if self.showoverlay:
            # get center color value
            color = rgb[240, 320]

            # set center marker
            rgb[240, 320] = np.array([255,0,255])

        if self.detectball:
            rgb = self.balldetector.detectDepth(rgb, depth)

        # generate opencv image
        img = cv.fromarray(np.array(rgb[:,:,::-1], dtype=np.uint8))


        if self.showoverlay:
            f = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0)
            # PutText(img, text, org, font, color)
            cv.PutText(img, 'Color: %s' % (color), (20,20) , f, (int(color[2]), int(color[1]), int(color[0])))
            cv.PutText(img, 'X', (320, 240) , f, (255, 255 , 255))

        # Display image
        cv.ShowImage('display', rgb_opencv)
        # cv.ShowImage('display', cv.fromarray(np.array(rgb[:,:,::-1])))
        # cv.ShowImage('display', depth_opencv)

if __name__ == '__main__':
    import sys

    filters = []
    for argv in sys.argv:
        if argv.startswith('--'):
            filters.append(argv[2:])

    dummymode = "--dummymode" in sys.argv or "-d" in sys.argv
    if dummymode:
        from KinectDummy import KinectDummy
        kinect = KinectDummy()
    else:
        try:
            from Kinect import Kinect
            kinect = Kinect()
        except ImportError:
            from KinectDummy import KinectDummy
            kinect = KinectDummy()
            dummymode = True;

    Kinector(kinect=kinect, filters=filters, dummymode=dummymode, record=False, canny=False, hough=False).loop()

