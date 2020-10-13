import unittest
from PIL import Image, ImageChops
import glob
import logging


class TestCompareImages(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(filename='image_compare.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def test_screens(self):
        screens = zip(glob.glob('screenshots/prod_*.png'), glob.glob('screenshots/test_*.png'))
        for prod, test in screens:
            with self.subTest():
                try:
                    img_prod = Image.open(prod).convert('RGB')
                    img_test = Image.open(test).convert('RGB')
                    diff = ImageChops.difference(img_prod, img_test)
                    self.assertFalse(bool(diff.getbbox()), f"{test} does not match {prod}")
                    logging.info(f'{test} MATCHES {prod}')
                except AssertionError as e:
                    identifier = prod[(prod.find('_') + 1):prod.find('.png')]
                    print(str(e))
                    logging.info(f'{test} DOES NOT match {prod}')
                    diff.save('screenshots/diff_' + identifier + '.png')


if __name__ == "__main__":
    unittest.main()
