import PyInstaller.__main__
import config
PyInstaller.__main__.run([
    'Aisle.py',
    '--onefile',
    f'--key {config.private.PYINSTALLER_PASSWD}'
])
