from setuptools import setup, find_packages
from rssbot import __version__
try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

requirements = parse_requirements("requirements.txt", session=PipSession())

setup(
    name="pubgate",
    description="Lightweight ActivityPub federator",
    author="autogestion",
    author_email="",
    url="https://github.com/autogestion/pubgate",
    version=__version__,
    packages=find_packages(),
    install_requires=[str(x.req) for x in requirements],
    license="BSD 3-Clause",
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Framework :: Sanic",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ),
    platforms="Python 3.6 and later."
)