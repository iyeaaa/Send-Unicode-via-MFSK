import play


def send_data():
    text = input("Type some text (only English and Number)\nUser input: ")
    play.send(text)


def receive_data():
    play.receive()


def main():
    while True:
        print('Morse Code over Sound with Noise')
        print('2024 Spring Data Communication at CNU')
        print('[1] Send morse code over sound (play)')
        print('[2] Receive morse code over sound (record)')
        print('[q] Exit')
        select = input('Select menu: ').strip().upper()
        if select == '1':
            send_data()
        elif select == '2':
            receive_data()
        elif select == 'Q':
            print('Terminating...')
            break


if __name__ == '__main__':
    main()
