import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edyay",
    version="0.0.1",
    author="Brian Lange",
    author_email="blange@ideo.com",
    description="EDYay is a package of scripts and modules for making EDA more easy, collaborative, and fun.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy==1.22.0',
        'pandas==1.0.0',
        'python-dateutil==2.8.1',
        'pytz==2019.3',
        'six==1.14.0',
        'PyYAML>=5.1.1',
        'cycler>=0.10',
        'pyparsing!=2.0.4,!=2.1.2,!=2.1.6,>=2.0.1',
        'kiwisolver>=1.0.1',
        'matplotlib==3.1.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

# packages is a list of all Python import packages that should be included in the distribution package. Instead of listing each package manually, we can use find_packages() to automatically discover all packages and subpackages. In this case, the list of packages will be example_pkg as that’s the only package present.
# classifiers gives the index and pip some additional metadata about your package. In this case, the package is only compatible with Python 3, is licensed under the MIT license, and is OS-independent. You should always include at least which version(s) of Python your package works on, which license your package is available under, and which operating systems your package will work on. For a complete list of classifiers, see https://pypi.org/classifiers/.