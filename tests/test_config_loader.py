from src.utils.config_loader import get_config, Config

def test_get_config_returns_same_instance():
    c1 = get_config()
    c2 = get_config()
    assert c1 is c2

def test_get_config_returns_config_instance():
    assert isinstance(get_config(), Config)