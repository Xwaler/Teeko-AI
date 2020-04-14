import os


def install():
    interpreter = input('\nInstalling requirement for ?\n0: pip\n1: conda\n>> ')

    if interpreter == '0':
        os.system('pip install pygame numpy torch==1.4.0+cpu torchvision==0.5.0+cpu '
                  '-f https://download.pytorch.org/whl/torch_stable.html')
    elif interpreter == '1':
        os.system('conda install numpy pygame pytorch torchvision cpuonly -c pytorch')
    else:
        install()


if __name__ == '__main__':
    install()
