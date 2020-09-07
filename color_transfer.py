import cv2
import numpy as np


class ColorTransfer:

    def __init__(self, source_image, target_image, transfer_name=None):
        self.source = cv2.imread(source_image)
        self.target = cv2.imread(target_image)
        self.target_name = target_image.split('/')
        self.transfer_name = transfer_name
        
        if (self.target_name[-1] is None or self.target_name[-1] is '') and (self.transfer_name is None):
            self.transfer_name = 'new_' + self.target_name[-2]
        elif self.transfer_name is None:
            self.transfer_name = 'new_' + self.target_name[-1]



    def image_color_lab(self):
        self.source = cv2.cvtColor(self.source, cv2.COLOR_BGR2LAB).astype('float32')
        self.target = cv2.cvtColor(self.target, cv2.COLOR_BGR2LAB).astype('float32')

    def image_stat(self, image):
        # Computing image stats
        (l, a, b) = cv2.split(image)
        (l_mean, l_std) = (l.mean(), l.std())
        (a_mean, a_std) = (a.mean(), a.std())
        (b_mean, b_std) = (b.mean(), b.std())

        return l_mean, l_std, a_mean, a_std, b_mean, b_std

    def transfer(self):
        # convert image source to L*a*b
        self.image_color_lab()

        # compute color statistics for the source and target images
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self.image_stat(self.source)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self.image_stat(self.target)

        # split target into L,a, b for further analysis, subtract it mean to achieve no deviation
        l, a, b = cv2.split(self.target)
        l -= lMeanTar
        a -= aMeanTar
        b -= bMeanTar

        # Scale with Std from source to achieve same deviation
        l = (lStdTar/lStdSrc) * l
        a = (aStdTar / aStdSrc) * a
        b = (bStdTar/bStdSrc) * b

        # Add source mean for correction
        l += lMeanSrc
        a += aMeanSrc
        b += bMeanSrc

        # Clip to 256 because of Color range
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Combine and convert back to RGB imagee
        transfer = cv2.merge([l, a, b])
        transfer = cv2.cvtColor(transfer.astype('uint8'), cv2.COLOR_LAB2BGR)

        cv2.imwrite(self.transfer_name, transfer)


