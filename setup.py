from setuptools import setup
setup(
    name='color-transfer',
    version='0.0.1',
    author='Abdulrahman Aminu',
    scripts=['color_transfer.py'],
    entry_points={
        'console_scripts': [
            'color-transfer = color_transfer:run'
        ]
    }
)
