"""
Basic tests for chimera_factory package initialization.
"""


def test_package_import():
    """Test that the package can be imported."""
    import chimera_factory
    assert chimera_factory.__version__ == "0.1.0"


def test_package_version():
    """Test that the package has a version attribute."""
    import chimera_factory
    assert hasattr(chimera_factory, "__version__")
    assert isinstance(chimera_factory.__version__, str)
