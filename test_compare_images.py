import unittest
from PIL import Image, ImageChops
import glob
import logging
from settings import Settings
from datetime import datetime

class TestCompareImages(unittest.TestCase):

    X_TOP_LIMITER = 50

    def setUp(self):
        self.settings = Settings()
        self.COLOR = self.settings.compare['box_color']

        now = datetime.now()
        log_time = now.strftime("%Y%m%d%H%M%S")
        logging.basicConfig(filename=f'logs/image_compare_{log_time}.log',
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def test_screens(self):
        screens = zip(glob.glob('screenshots/prod_*.png'), glob.glob('screenshots/test_*.png'))
        for prod, test in screens:
            img_prod = self.find_frame(Image.open(prod).convert('RGB'))
            img_test = self.find_frame(Image.open(test).convert('RGB'))
            diff = ImageChops.difference(img_prod, img_test)
            try:
                with self.subTest(f"{test} does not match {prod}"):
                    self.assertFalse(bool(diff.getbbox()))
            except AssertionError:
                identifier = prod[(prod.find('_') + 1):prod.find('.png')]
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

        for y in range(1, height):
            for x in range(1, self.X_TOP_LIMITER):
                if orig_pix_map[x, y] == self.COLOR:
                    box.append(x)
                    box.append(y)
                    box.append(get_right(x, y))
                    box.append(get_bottom(x, y))
                    done = True
                    break
            if done:
                break
        if 'padding_offset' in self.settings.compare.keys():
            box[0] += self.settings.compare['padding_offset'][0]
            box[1] += self.settings.compare['padding_offset'][1]
            box[2] -= self.settings.compare['padding_offset'][2]
            box[3] -= self.settings.compare['padding_offset'][3]

        return orig_image.crop(box)

if __name__ == "__main__":
    unittest.main()
