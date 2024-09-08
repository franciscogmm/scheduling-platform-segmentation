import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scheduling_platform_segmentation",
    version="0.0.1",
    author="francsicogmm",
    author_email="franciscogm.mendoza@gmail.com",
    description="Scheduling Platform Segmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/franciscogmm/scheduling-platform-segmentation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)