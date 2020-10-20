import unittest
from PIL import Image, ImageChops
import glob
import logging
from settings import Settings
from datetime import datetime


class TestCompareImages(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

        now = datetime.now()
        log_time = now.strftime("%d%m%Y%H%M%S")
        logging.basicConfig(filename=f'image_compare_{log_time}.log',
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

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
            while orig_pix_map[x, y] == self.settings.compare['box_color']:
                x += 1
            return x

        def get_bottom(x, y):
            while orig_pix_map[x, y] == self.settings.compare['box_color']:
                y += 1
            return y

        orig_pix_map = orig_image.load()
        width, height = orig_image.size

        box = []
        done = False

        for y in range(height):
            for x in range(width):
                if orig_pix_map[x, y] == self.settings.compare['box_color']:
                    box.append(x)
                    box.append(y)
                    box.append(get_right(x, y))
                    box.append(get_bottom(x, y))
                    done = True
                    break
            if done:
                break
        if 'padding_offset' in self.settings.compare.keys():
            box[0] += self.settings.compare['padding_offset']
            box[1] += self.settings.compare['padding_offset']
            box[2] -= self.settings.compare['padding_offset']
            box[3] -= self.settings.compare['padding_offset']

        return orig_image.crop(box)

if __name__ == "__main__":
    unittest.main()
