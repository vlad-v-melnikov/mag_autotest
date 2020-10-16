from settings import Settings
from pprint import pprint


def main():
    settings = Settings()
    a = next(iter(settings.plan['area']))
    print(a)


if __name__ == '__main__':
    main()

