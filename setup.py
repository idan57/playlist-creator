import setuptools

try:
    with open("pipplusplus/README.md", "r") as fh:
        long_description = fh.read()
except Exception:
    with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="playlist-creator",
    version="0.0.1",
    author="Idan Cohen,Ziv Zaarur",
    include_package_data=True,
    author_email="idan57@gmail.com,zivza94@gmail.com",
    description="Create your playlist with us!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idan57/playlist-creator",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'gekko',
        'matplotlib',
        'xlwt',
        'mutagen',
        'spotipy',
        'country-converter'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)