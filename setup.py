import os, re
from setuptools import setup, find_packages

try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

requirements = parse_requirements("requirements.txt", session=PipSession())


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="pubgate",
    description="Lightweight ActivityPub federator",
    author="autogestion",
    author_email="",
    url="https://github.com/autogestion/pubgate",
    version=get_version("pubgate"),
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