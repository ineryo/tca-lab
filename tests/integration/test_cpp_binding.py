import tca


def test_cpp_backend_is_available():
    assert tca.backend_name() == "tca-cpp"
