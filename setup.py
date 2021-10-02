import setuptools

setuptools.setup(
    name="pageplot",
    version="0.0.1",
    description="",
    url="",
    author="Josh Borrow",
    author_email="josh@joshborrow.com",
    packages=setuptools.find_packages(),
    long_description="",
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["attrs", "h5py", "velociraptor", "matplotlib", "numpy", "scipy", "unyt"],
)
