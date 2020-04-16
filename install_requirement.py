from subprocess import Popen, PIPE, DEVNULL


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
            print('Conda not found, exiting...')
            quit()

    Popen([interpreter, 'install', 'pygame', 'numpy'])

    p = Popen([interpreter, 'list'], stdout=PIPE)
    stdout, _ = p.communicate()

    if b'torch' in stdout:
        print('Requirement already satisfied: pytorch')

    else:
        print('Installing pytorch...')
        if interpreter == 'pip':
            Popen([interpreter, 'install', 'torch==1.4.0+cpu', 'torchvision==0.5.0+cpu',
                   '-f', 'https://download.pytorch.org/whl/torch_stable.html'])

        else:
            Popen([interpreter, 'install', 'pytorch', 'torchvision', 'cpuonly', '-c', 'pytorch'])


if __name__ == '__main__':
    install()
