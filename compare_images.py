import unittest
from PIL import Image, ImageChops
import glob
import logging
from modules.settings_compare import SettingsCompare
from modules.jirainterface import JiraInterface
from datetime import datetime


class TestCompareImages(unittest.TestCase):

    X_RIGHT_LIMITER_SINGLE = 50

    def setUp(self):
        self.settings = SettingsCompare()
        self.COLOR_SINGLE = self.settings.compare['box_color']
        self.COLOR_FOUR = self.settings.compare['box_color_four']
        self.jira_interface = JiraInterface(self.settings.driver)

        now = datetime.now()
        log_time = now.strftime("%Y%m%d%H%M%S")
        logging.basicConfig(filename=f'logs/image_compare_{log_time}.log',
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def test_screens(self):
        prod_screens = glob.glob('screenshots/prod_*.png')
        test_screens = glob.glob('screenshots/test_*.png')
        print(f'{len(prod_screens)} images from PROD, {len(test_screens)} from TEST.')
        logging.info(f'{len(prod_screens)} images from PROD, {len(test_screens)} from TEST.')

        test_case = None
        if self.settings.jira:
            test_case = self.jira_interface.create_testcase_for_diff()

        try:
            self.assertNotEqual(len(test_screens), 0,
                                "No screenshots from TEST. Nothing to compare.")
            self.assertNotEqual(len(test_screens), 0,
                                "No screenshots from PROD. Nothing to compare.")
        except AssertionError as e:
            logging.error("Zero screenshots from TEST and/or PROD")
            if self.settings.jira:
                self.jira_interface.report_diff_failure(test_case, "Zero screenshots from TEST and/or PROD", )
            raise e

        try:
            self.assertEqual(len(test_screens), len(prod_screens),
                             "Number of screenshots for test and prod is DIFFERENT")
        except AssertionError as e:
            logging.error("Number of screenshots for test and prod is DIFFERENT")
            if self.settings.jira:
                self.jira_interface.report_diff_failure(test_case, "Number of screenshots for test and prod is DIFFERENT", )
            raise e

        screens = zip(prod_screens, test_screens)
        results = []
        for prod, test in screens:
            img_prod = self.find_frame(Image.open(prod).convert('RGB'), prod, test_case)
            img_test = self.find_frame(Image.open(test).convert('RGB'), test, test_case)
            diff = ImageChops.difference(img_prod, img_test)
            with self.subTest(f"{test} DOES NOT MATCH {prod}"):
                try:
                    self.assertFalse(bool(diff.getbbox()))
                    results.append("Pass")
                except AssertionError as e:
                    identifier = prod[(prod.find('_') + 1):prod.find('.png')]
                    logging.error(f'{test} DOES NOT match {prod}')
                    diff.save('screenshots/diff_' + identifier + '.png')
                    results.append("Fail")
                    raise e

        # pushing results of image comparison to Zephyr Scale
        if self.settings.jira:
            print("Pushing results to Zephyr Scale on Jira...")
            screens = [screen[17:] for screen in prod_screens]
            self.jira_interface.add_testcase_steps_for_images(test_case, screens)
            self.jira_interface.send_execution_image_diff(test_case, results)
            print("Done.")

    def find_frame(self, orig_image, img_name, test_case) -> Image:
        orig_pix_map = orig_image.load()
        width, height = orig_image.size

        # setting
        target = {
            'top': 1,
            'left': 1,
            'bottom': height,
            'right': self.X_RIGHT_LIMITER_SINGLE,
            'color': tuple(self.COLOR_SINGLE)
        }

        # finding single
        box = self.search_for_it(target, orig_pix_map)

        # finding_four:
        if len(box) == 0:
            img_width = 1024
            tolerance = 20
            target = {
                'top': 1,
                'left': int(width/2 - img_width/2 - tolerance),
                'bottom': height,
                'right': int(width/2 - img_width/2 + tolerance),
                'color': tuple(self.COLOR_FOUR[self.settings.driver])
            }
            box = self.search_for_it(target, orig_pix_map, four_images=True)

            # ---code to check if there is something wrong with finding the box---
            # target = orig_image.crop((target['left'], target['top'], target['right'], target['bottom']))
            # target.save('screenshots/target.png')
            # to_save = orig_image.crop(box)
            # to_save.save('screenshots/box.png')

        try:
            self.assertEqual(len(box), 4, f"Could not find borders of the frame for {img_name}.")
        except AssertionError as e:
            logging.error(f"Could not find borders of the frame for {img_name}.")
            self.jira_interface.report_diff_failure(test_case, f"Could not find borders of the frame for {img_name}.")
            raise e

        return orig_image.crop(box)

    def search_for_it(self, target: dict, orig_pix_map, four_images=False) -> list:
        def get_right(x, y):
            while orig_pix_map[x, y] == target['color']:
                x += 1
            return x

        def get_bottom(x, y):
            while orig_pix_map[x, y] == target['color']:
                y += 1
            return y

        box = []
        done = False
        for y in range(target['top'], target['bottom']):
            for x in range(target['left'], target['right']):
                if orig_pix_map[x, y] == target['color']:
                    box.append(x)
                    box.append(y)
                    box.append(get_right(x, y))
                    box.append(get_bottom(x, y))
                    done = True
                    break
            if done:
                break

        if self.settings.compare['use_padding'] and len(box) > 0 and not four_images:
            box[0] += self.settings.compare['padding_offset'][0]
            box[1] += self.settings.compare['padding_offset'][1]
            box[2] -= self.settings.compare['padding_offset'][2]
            box[3] -= self.settings.compare['padding_offset'][3]
        return box


if __name__ == "__main__":
    unittest.main()
