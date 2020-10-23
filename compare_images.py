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
        prod_screens = glob.glob('screenshots/prod_*.png')
        test_screens = glob.glob('screenshots/test_*.png')
        try:
            self.assertEqual(len(test_screens), len(prod_screens), "Number of screenshots for test and prod is DIFFERENT")
        except AssertionError as e:
            logging.error("Number of screenshots for test and prod is DIFFERENT")
            raise e

        screens = zip(prod_screens, test_screens)
        for prod, test in screens:
            img_prod = self.find_frame(Image.open(prod).convert('RGB'), prod)
            img_test = self.find_frame(Image.open(test).convert('RGB'), test)
            diff = ImageChops.difference(img_prod, img_test)
            with self.subTest(f"{test} DOES NOT MATCH {prod}"):
                try:
                    self.assertFalse(bool(diff.getbbox()))
                except AssertionError as e:
                    identifier = prod[(prod.find('_') + 1):prod.find('.png')]
                    logging.error(f'{test} DOES NOT match {prod}')
                    diff.save('screenshots/diff_' + identifier + '.png')
                    raise e

    def find_frame(self, orig_image, img_name) -> Image:
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

        if self.settings.compare['use_padding']:
            box[0] += self.settings.compare['padding_offset'][0]
            box[1] += self.settings.compare['padding_offset'][1]
            box[2] -= self.settings.compare['padding_offset'][2]
            box[3] -= self.settings.compare['padding_offset'][3]

        try:
            self.assertEqual(len(box), 4, f"Could not find borders of the frame for {img_name}.")
        except AssertionError as e:
            logging.error(f"Could not find borders of the frame for {img_name}.")
            raise e

        return orig_image.crop(box)

if __name__ == "__main__":
    unittest.main()
