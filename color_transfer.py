import cv2
import numpy as np
import argparse
import glob
import sys
import os.path
from pathlib import Path


class ColorTransfer:

    def __init__(self, source_image, target_image, transfer_name=None):
        #Initialization of attributes
        self.source = cv2.imread(source_image)
        self.target = cv2.imread(target_image)
        self.transfer_name = transfer_name

        # Protected
        self._target_name = target_image.split('/')

        # Check if transfer name is not None or empty string. Set to filtered if empty
        if self.transfer_name is None or self.transfer_name == '':
            self.transfer_name = ('/').join(self._target_name[:-1]) + '/filtered_' + self._target_name[-1]
        else:
            self.transfer_name = ('/').join(self._target_name[:-1]) + '/' +self.transfer_name + '.png'


    # Conversion of Image to equivalent Human-eye perception L*a*b
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

# Function to handle multiple file types in target folder
def file_color_transfer(source_image:str, target_file:str, file_type:tuple):
    file = target_file
    types = file_type
    images = []
    for image_type in types: # Retrieves all the images in the supplied directory based on the file_type supplied
        images.extend(glob.glob(file + image_type))

    for image in images: # Applies the ColorTransfer class from above to all the images in the file.
        color_transfer = ColorTransfer(source_image, image)
        color_transfer.transfer()


# function to determine if image path or file path is correct when using interactive cli
def path_receiver_and_checker(name: str):
    """
    name: String of what you are requesting for e.g source image, or Target Image, or Target File
    """
    path = input(f'Enter path to {name}: ')
    if path != '':
        path_verifier = Path(path).exists()
    elif source_image == '':
        path_verifier = False

    while not path_verifier:
        path = input(f"\n Wrong or Empty Path inputted. Enter a correct path to {name}: ")

    return path


# Create Command line arguement parser, please endeavor to supply either -t target_image or -f target_file but not both.
ag = argparse.ArgumentParser(description='parser for command line')
ag.add_argument('-s', '--source_image', default=argparse.SUPPRESS, help='Path to Source Image')
ag.add_argument('-t', '--target_image', default=argparse.SUPPRESS, help='Path to Target Image')
ag.add_argument('-f', '--target_file', default=argparse.SUPPRESS, help='Path to Target file with many images')
args = vars(ag.parse_args())

# Check if command line was parsed, to be used for decision make below
check_source_image = isinstance(args.get('source_image', False), str)
check_target_image = isinstance(args.get('target_image', False), str)
check_target_file = isinstance(args.get('target_file', False), str)

def run():
    # Checking if command line arguements were provided and also verify that only a targert image or target file was provided.
    if check_source_image and (check_target_image ^ check_target_file):
        try:
            source_image = args['source_image']

            if args.get('target_image', False):
                target_image = args['target_image']
                color_transfer = ColorTransfer(source_image, target_image)
                color_transfer.transfer()

            elif args.get('target_file', False):
                target_folder = args['target_file']
                file_color_transfer(source_image, target_folder, ('/*.jpg', '/*.png'))

        except Exception as e:
            print('\nAn error occured', e, 'please retry\n')

    # Switch to Interactive Command line if arguments werent provided above
    else:
        print('\n...Opting for the interactive CLI method due to an error\n')

        try:
            source_image = path_receiver_and_checker('Source Image')

            decision = input('\nIs a single image or files containing images. Please input "S" for single image or "F" for '
                             'file: ').upper()

            if decision == 'S':
                target_image = path_receiver_and_checker('Target Image')
                target_name = input('\nEnter name for new image or press Enter: ')
                color_transfer = ColorTransfer(source_image, target_image, transfer_name=target_name)
                color_transfer.transfer()

            elif decision == 'F':
                target_folder = path_receiver_and_checker('Target Folder')
                file_color_transfer(source_image, target_folder, ('/*.jpg', '/*.png'))

            else:
                raise TypeError

        except Exception as e:
            print('\nAn error occured: ', e, ', please retry\n')

if __name__ == '__main__':
    run()