from setuptools import setup


def readme():
    """Open up the readme and use the text for the long description."""
    with open("README.md") as f:
        return f.read()


setup(
    name="yabp",
    version="1.0.0",
    description="Yet Another Bus Pirate",
    long_description=readme(),
    author="David Patterson",
    url="https://github.com/jdpatt/yabp",
    packages=[
        "yabp",
    ],
    include_package_data=True,
    install_requires=["pyserial"],
    license="MIT",
    zip_safe=False,
    keywords="yabp",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
