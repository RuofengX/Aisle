import PyInstaller.__main__
import random
import os


class Builder(object):
    def __init__(self, name, icon):
        self.name = name
        self.key = ''.join(random.sample('1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM', 16))

        self.icon = icon
        self.getIcon()

        self.startArgs = [
            self.name,
            '--onefile',
            f'--key={self.key}',
            f'-i={self.icon}'
        ]

    def getIcon(self):
        self.icon = ''
        return ''

    def build(self):
        PyInstaller.__main__.run(self.startArgs)


class BuilderOnWindows(Builder):
    """
    目前只能在Windows平台编译，见下文：  |  同时Linux平台使用os.fork()也有问题。
    https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    Warning
    The 'spawn' and 'forkserver' start methods cannot currently be used with “frozen” executables (i.e., binaries produced by packages like PyInstaller and cx_Freeze) on Unix. The 'fork' start method does work.
    """
    def __init__(self, name, icon):
        super(BuilderOnWindows, self).__init__(name, icon)

    def getIcon(self):
        self.icon = os.path.join('img', self.icon)


if __name__ == '__main__':
    buildList = [
        'AisleCL.py'
    ]
    for i in buildList:
        build0 = BuilderOnWindows(name=i, icon='a7rz2-w8k73-001.ico')
        build0.build()
