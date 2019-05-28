from distutils.core import setup

from setuptools import find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='LogClouseau',
    packages=find_packages(exclude=['tests']),
    version='0.1.0',
    description='LogClouseau inspects your logs, extracts information and '
                'sends alerts according to your conditions',
    long_description=readme,
    author='Alessandro Balasco',
    author_email='alessandro.balasco@gmail.com',
    url='https://github.com/palicao/logclouseau',
    keywords=[
        'log',
        'inspect',
        'alert',
    ],
    install_requires=[
        'toml',
        'slackclient',
        'tailer',
        'click',
        'expressions @ git+https://github.com/palicao/expressions@079359ee8111769ca18ade25aad4de0133e1bfc0#egg=expressions'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    entry_points={
        'console_scripts': ['logclouseau=src.command:main'],
    }
)
