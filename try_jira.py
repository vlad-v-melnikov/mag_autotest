from modules.settings_jira import SettingsJira

def main():
    print('Checking Jira connection.')

    jira = SettingsJira()

    print('Connection OK.')


if __name__ == '__main__':
    main()