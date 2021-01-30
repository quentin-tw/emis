from setuptools import setup

setup(
    name='emis_app',
    packages=['emis_app'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)