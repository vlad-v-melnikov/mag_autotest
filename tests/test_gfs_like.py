import unittest
from modules.dimensions import WINDOW_WIDTH
from modules.dimensions import WINDOW_HEIGHT
from modules.gfs_like import GfsLike
from modules.settings import Settings

from selenium import webdriver


class TestGfsLike(unittest.TestCase):
    def setUp(self) -> None:
        filename = 'json/settings_default.json'
        self.settings = Settings(filename=filename)
        self.driver = webdriver.Firefox()
        self.site = "https://mag.ncep.noaa.gov"
        self.driver.get(self.site)
        handles = {'test': self.driver.window_handles[0]}
        self.gfs = GfsLike('GFS', self.driver, handles, filename=filename)

    def test_change_dimensions(self):
        orig_width = 1980
        orig_height = 1100
        self.driver.set_window_size(orig_width, orig_height)

        old_dim, _ = self.gfs.change_dim_and_pos({'width': WINDOW_WIDTH,
                                                  'height': WINDOW_HEIGHT
                                                  },
                                                 self.driver.get_window_position())
        new_dim = self.driver.get_window_size()

        self.assertEqual(old_dim['width'], orig_width)
        self.assertEqual(old_dim['height'], orig_height)
        self.assertGreaterEqual(new_dim['width'], WINDOW_WIDTH, "The window width is too small")
        self.assertGreaterEqual(new_dim['height'], WINDOW_HEIGHT, "The window height is too small")

    def tearDown(self) -> None:
        self.driver.close()


if __name__ == '__main__':
    unittest.main()
