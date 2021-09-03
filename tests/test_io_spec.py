"""
Tests basic understanding of pydantic.
"""

from pageplot.io.spec import IOSpecification

def test_IOSpecification():
    io_spec = IOSpecification(filename="test.csv")