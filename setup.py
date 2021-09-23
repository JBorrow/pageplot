import setuptools

setuptools.setup(
    name="pageplot",
    version="0.0.1",
    description="",
    url="",
    author="Josh Borrow",
    author_email="josh@joshborrow.ciom",
    packages=setuptools.find_packages(),
    long_description="",
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=["attrs", "h5py", "velociraptor", "matplotlib", "numpy", "scipy", "unyt"],
)