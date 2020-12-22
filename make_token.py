import base64
import getpass


def main():
    username = input('Please enter your JIRA name: ')
    password = getpass.getpass('Please enter your JIRA password (no letters are echoed): ')
    token = base64.b64encode(f'{username}:{password}'.encode('ascii'))
    with open('token.txt', 'wb') as file:
        file.write(token)

    print(f'Your token {token} is saved to token.txt')


if __name__ == '__main__':
    main()