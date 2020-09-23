import cv2
import numpy as np
import argparse
import glob
import sys


class ColorTransfer:

    def __init__(self, source_image, target_image, transfer_name=None):

        self.source = cv2.imread(source_image)
        self.target = cv2.imread(target_image)
        self.transfer_name = transfer_name

        # Protected
        self._target_name = target_image.split('/')

        if self.transfer_name is None or self.transfer_name == '':
            self.transfer_name = ('/').join(self._target_name[:-1]) + '/filtered_' + self._target_name[-1]
        else:
            self.transfer_name = ('/').join(self._target_name[:-1]) + '/' +self.transfer_name + '.png'



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
        (l_mean_src, l_std_src, a_mean_src, a_std_src, b_mean_src, b_std_src) = self.image_stat(self.source)
        (l_mean_tar, l_std_tar, a_mean_tar, a_std_tar, b_mean_tar, b_std_tar) = self.image_stat(self.target)

        # split target into L,a, b for further analysis, subtract it mean to achieve no deviation
        l, a, b = cv2.split(self.target)
        l -= l_mean_tar
        a -= a_mean_tar
        b -= b_mean_tar

        # Scale with Std from source to achieve same deviation
        l = (l_std_tar/l_std_src) * l
        a = (a_std_tar / a_std_src) * a
        b = (b_std_tar/b_std_src) * b

        # Add source mean for correction
        l += l_mean_src
        a += a_mean_src
        b += b_mean_src

        # Clip to 256 because of Color range
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Combine and convert back to RGB imagee
        transfer = cv2.merge([l, a, b])
        transfer = cv2.cvtColor(transfer.astype('uint8'), cv2.COLOR_LAB2BGR)

        # Wirte and save new image
        cv2.imwrite(self.transfer_name, transfer)


if __name__ == '__main__':
    try:
        source_image = input('Enter path to source/primary image: ')
        decision = input('\nIs a single image or files containing images. Please input "S" for single image or "F" for '
                         'file: ').upper()
        if decision == 'S':
            target_image = input('\nEnter path to Target image: ')
            target_name = input('\nEnter name for new image or press Enter: ')
            color_transfer = ColorTransfer(source_image, target_image, transfer_name=target_name)
            color_transfer.transfer()

        elif decision == 'F':
            target_folder = input('\nEnter path to Target folder: ')
            images = []
            for png in glob.glob(target_folder + '/*.png'):
                images.append(png)
            for jpg in glob.glob(target_folder + '/*.jpg'):
                images.append(jpg)

            for image in images:
                color_transfer = ColorTransfer(source_image, image)
                color_transfer.transfer()
        else:
            raise TypeError

    except Exception as e:
        print('An error occured', e, 'please retry')






