import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hodor",
    version="1.0",
    author="Adrian Dolha",
    packages=[],
    author_email="adriandolha@eyahoo.com",
    description="Authentication and authorization service",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
