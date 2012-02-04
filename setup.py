import os
from setuptools import setup
import shaker

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "shaker",
    packages = ["shaker"],
    version = shaker.__version__,
    description = "EC2 Salt Minion Launcher",
    author = "Jeff Bauer",
    author_email = "jbauer@rubic.com",
    url = "https://github.com/rubic/shaker",
    keywords = ["salt", "ec2", "aws"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        ],
    long_description = read('README.rst'),
    scripts=['scripts/shaker',
             'scripts/shaker-terminate',
         ],
)
