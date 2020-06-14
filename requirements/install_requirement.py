from subprocess import Popen, DEVNULL


def install():
    interpreter = None
    try:
        Popen(['pip'], stdout=DEVNULL)
        interpreter = 'pip'
    except FileNotFoundError:
        print('Pip not found')
        try:
            Popen(['conda'], stdout=DEVNULL)
            interpreter = 'conda'
        except FileNotFoundError:
            print('Conda not found\nExiting.')
            quit()

    Popen([interpreter, 'install', 'pygame', 'numpy', 'tqdm'])


if __name__ == '__main__':
    install()
