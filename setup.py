from setuptools import setup

setup(
    name='plgspl',
    version='0.0.0',
    packages=['plgspl'],
    entry_points={
        'console_scripts': [
            'plgspl = plgspl.plgspl:main'
        ]
    })
