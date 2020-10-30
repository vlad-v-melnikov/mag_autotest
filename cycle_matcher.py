from settings import Settings


class CycleMatcher:
    def __init__(self, model, driver, handles):
        self.settings = Settings()
        self.plan = self.settings.plan[model]
        self.driver = driver
        self.handles = handles

    def match_now(self):
        pass