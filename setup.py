from distutils.core import setup

setup(
    name = "shaker",
    packages = ["shaker"],
    version = "0.1.0",
    description = "EC2 Salt Minion Launcher",
    author = "Jeff Bauer",
    author_email = "jbauer@rubic.com",
    url = "http://python.net/crew/jbauer",
    download_url = "http://python.net/crew/jbauer/shaker-0.1.0.tgz",
    keywords = ["salt", "ec2", "aws"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        ],
    long_description = """\
Create and Launch Salt Minions on EC2
-------------------------------------

More description to follow ...
 - salt minions are created and launched
 - template-based (Jinja2)
 - supports Ubuntu, Debian and soon (Fedora)
"""
)
