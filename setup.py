from setuptools import setup

def readme():
    """Open up the readme and use the text for the long description."""
    with open("README.md") as f:
        return f.read()


setup(
    name="yabp",
    version="0.1.0",
    description="Yet Another Bus Pirate",
    long_description=readme(),
    author="David Patterson",
    url="https://github.com/jdpatt/yabp",
    entry_points={
        'console_scripts': [
            'yabp=yabp.cli:main',
        ],
    },
    packages=[
        "yabp",
    ],
    package_dir={"yabp": "yabp"},
    include_package_data=True,
    install_requires=[
    ],
    license="MIT",
    zip_safe=False,
    keywords="yabp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
