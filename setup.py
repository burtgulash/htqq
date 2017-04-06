from setuptools import setup
from htqq import __version__

setup(name="htqq",
    version=__version__,
    description="HTMq html extractor",
    author="Burtgulash",
    author_email="burtgulas@gmail.com",
    packages=["htqq"],
    scripts=["scripts/htqq"],
    install_requires=[
        "docopt",
        "lxml",
    ],
    entry_points={
        "console_scripts": [
            "htqq=htqq.htqq:main",
        ]
    },
)
