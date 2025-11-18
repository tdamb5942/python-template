from src.smoke import smoke_test


def test_smoke():
    """Verifies that the testing framework and imports are set up correctly."""
    assert smoke_test() is True
