import unittest
from PIL import Image, ImageChops
import glob
import logging


class TestCompareImages(unittest.TestCase):

    COLOR = (102, 102, 102)

    def setUp(self):
        logging.basicConfig(filename='image_compare.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def test_screens(self):
        screens = zip(glob.glob('screenshots/prod_*.png'), glob.glob('screenshots/test_*.png'))
        for prod, test in screens:
            with self.subTest():
                try:
                    img_prod = self.find_frame(Image.open(prod).convert('RGB'))
                    img_test = self.find_frame(Image.open(test).convert('RGB'))
                    diff = ImageChops.difference(img_prod, img_test)
                    self.assertFalse(bool(diff.getbbox()), f"{test} does not match {prod}")
                    logging.info(f'{test} MATCHES {prod}')
                except AssertionError as e:
                    identifier = prod[(prod.find('_') + 1):prod.find('.png')]
                    print(str(e))
                    logging.info(f'{test} DOES NOT match {prod}')
                    diff.save('screenshots/diff_' + identifier + '.png')

    def find_frame(self, orig_image) -> Image:
        def get_right(x, y):
            while orig_pix_map[x, y] == self.COLOR:
                x += 1
            return x

        def get_bottom(x, y):
            while orig_pix_map[x, y] == self.COLOR:
                y += 1
            return y

        orig_pix_map = orig_image.load()
        width, height = orig_image.size

        box = []
        done = False

        for y in range(height):
            for x in range(width):
                if orig_pix_map[x, y] == self.COLOR:
                    print(x, y)
                    box.append(x)
                    box.append(y)
                    box.append(get_right(x, y))
                    box.append(get_bottom(x, y))
                    done = True
                    break
            if done:
                break

        return orig_image.crop(box)

if __name__ == "__main__":
    unittest.main()
