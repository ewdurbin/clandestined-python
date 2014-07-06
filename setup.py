
from distutils.core import setup

requirements = []
test_requirements = []

setup(
    name='clandestiny',
    version='1.0.0a',
    author="Ernest W. Durbin III",
    author_email='ewdurbin@gmail.com',
    description='rendezvous hashing implementation based on murmur3 hash',
    url='https://github.com/ewdurbin/clandestiny',
    packages=['clandestine'],
    scripts=[],
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
)

