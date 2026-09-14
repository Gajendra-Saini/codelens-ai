from app.core.config import settings


def test_settings_defaults():
    assert settings.app_name == "CodeLens AI Local"
    assert settings.environment == "development"