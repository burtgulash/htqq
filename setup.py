from setuptools import setup
from htmq import __version__

setup(name="htmq",
    version=__version__,
    description="HTMq html extractor",
    author="Burtgulash",
    author_email="burtgulas@gmail.com",
    packages=["htmq"],
    scripts=["scripts/htmq"],
    install_requires=[
        "docopt",
        "lxml",
    ],
    entry_points={
        "console_scripts": [
            "htmq=htmq.htmq:main",
        ]
    },
)
