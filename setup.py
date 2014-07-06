
from distutils.core import setup
from distutils.core import Extension

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
    ext_modules=[Extension('clandestine._murmur3', ['ext/_murmur3.c'])],
    scripts=[],
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
)

