import unittest

from air_pollution.config.settings import get_env, get_mongodb_config


class SettingsTest(unittest.TestCase):
    def test_get_env_returns_default_for_missing_or_empty_value(self):
        self.assertEqual(get_env("DB_URI", "mongodb://default", {}), "mongodb://default")
        self.assertEqual(get_env("DB_URI", "mongodb://default", {"DB_URI": ""}), "mongodb://default")

    def test_get_env_returns_configured_value(self):
        result = get_env("DB_URI", "mongodb://default", {"DB_URI": "mongodb://custom:27017"})

        self.assertEqual(result, "mongodb://custom:27017")

    def test_get_mongodb_config_uses_defaults(self):
        result = get_mongodb_config({})

        self.assertEqual(result["uri"], "mongodb://mongodb:27017")
        self.assertEqual(result["database"], "air-pollution")

    def test_get_mongodb_config_uses_environment_values(self):
        result = get_mongodb_config({"DB_URI": "mongodb://localhost:27017", "DB_NAME": "test-db"})

        self.assertEqual(result["uri"], "mongodb://localhost:27017")
        self.assertEqual(result["database"], "test-db")


if __name__ == "__main__":
    unittest.main()
