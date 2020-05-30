from setuptools import setup

setup(
    name='plgspl',
    version='0.0.0',
    packages=['plgspl'],
    install_requires=['fpdf', 'pandas'],
    entry_points={
        'console_scripts': [
            'plgspl = plgspl.plgspl:main'
        ]
    },
    package_data={'plgspl': ['__defaults.json']},
    include_package_data=True)
