from setuptools import setup

VERSION = "0.1.0"


def load_long_description():
    with open("README.md", "r") as fh:
        return fh.read()


if __name__ == "__main__":
    setup(
        name="pyacker",
        version=VERSION,
        description="HCP Packer API client",
        long_description=load_long_description(),
        long_description_content_type="text/markdown",
        author="Jeffrey Hogan",
        url="https://github.com/jeffwecan/pyacker",
        keywords=["hcp", "packer", "api", "client", "pyacker"],
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        packages=["pyacker"],
        python_requires=">=3.8",
        install_requires=[
            "basic-api[adapter]",
            "requests",
        ],
    )
