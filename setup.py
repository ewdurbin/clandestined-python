
from distutils.core import setup
from distutils.core import Extension

extra_compile_args = ["-Wno-error=declaration-after-statement"]

requirements = []
test_requirements = []

setup(
    name='clandestined',
    version='1.0.0a',
    author="Ernest W. Durbin III",
    author_email='ewdurbin@gmail.com',
    description='rendezvous hashing implementation based on murmur3 hash',
    url='https://github.com/ewdurbin/clandestined-python',
    packages=['clandestined'],
    ext_modules=[Extension('clandestined._murmur3', ['ext/_murmur3.c'],
                           extra_compile_args=extra_compile_args)],
    scripts=[],
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
)

