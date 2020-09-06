import cv2
import numpy


class ColorTransfer:

    def __init__(self, source_image, target_image):
        self.source = cv2.imread(source_image)
        self.target = cv2.imread(target_image)

    def image_color_lab(self):
        self.source = cv2.cvtColor(self.source, cv2.COLOR_BGR2LAB)
        self.target = cv2.cvtColor(self.target, cv2.COLOR_BGR2LAB)

    def image_stat(self, image):
        # Computing image stats
        (l, a, b) = cv2.split(image)
        (l_mean, l_std) = (l.mean(), l.std())
        (a_mean, a_std) = (a.mean(), a.std())
        (b_mean, b_std) = (b.mean(), b.std())

        return l_mean, l_std, a_mean, a_std, b_mean, b_std
