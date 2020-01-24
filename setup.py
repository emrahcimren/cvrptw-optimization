import pathlib
from setuptools import setup, find_packages


def parse_requirements(filename):
    '''
    Function to parse requirements.txt
    :param filename:
    :return:
    '''

    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements('requirements.txt')
reqs = install_reqs

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="cimren-cvrptw-optimization",
    version="1.0.0",
    description="CVRPTW Optimization Models",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/emrahcimren/cvrptw-optimization",
    author="cimren",
    author_email="cimren.1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["cvrptw_optimization", "cvrptw_optimization/src"],
    include_package_data=True,
    install_requires=reqs,
    #entry_points={
    #    "console_scripts": [
    #        "realpython=reader.__main__:main",
    #    ]
    #},
)
