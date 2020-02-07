from setuptools import setup

setup(
    name='FluorSeg',
    version='0.0.26dev',
    packages=['fluorseg', 'fluorseg.test'],
    author='Dan MacLean',
    author_email='dan.maclean@tsl.ac.uk',
    url="https://github.com/TeamMacLean/fluorseg",
    license='LICENSE.txt',
    description="Segment regions from fluorescence images",
    long_description=open('README.txt').read(),
    python_requires='>=3.6.7',
    install_requires=[
        "javabridge >= 1.0.14",
        "python-bioformats >= 1.5.2",
        "matplotlib >= 3.0.1",
        "numpy >= 1.5.3",
        "read-roi >= 1.4.2",
        "pillow >= 5.3.0",
        "scipy >= 1.1.0",
        "scikit-image >= 0.14.1",
    ],
)