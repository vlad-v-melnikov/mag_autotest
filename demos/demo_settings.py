from modules.settings import Settings


def main():
    settings = Settings()
    a = next(iter(settings.plan['area']))
    print(a)


if __name__ == '__main__':
    main()

