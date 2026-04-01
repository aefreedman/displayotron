import json

import displayotron_common as common


def test_clamp_limits_values():
    assert common.clamp(-1, 0, 10) == 0
    assert common.clamp(11, 0, 10) == 10
    assert common.clamp(6, 0, 10) == 6


def test_default_settings_shape():
    settings = common.default_settings()
    assert settings["theme_index"] == 0
    assert settings["brightness"] == 70
    assert settings["contrast"] == 45
    assert settings["status_service_enabled"] is True
    assert settings["clock_blink_colon"] is True


def test_normalize_settings_non_dict_returns_defaults():
    assert common.normalize_settings(None) == common.default_settings()
    assert common.normalize_settings([]) == common.default_settings()


def test_normalize_settings_clamps_and_coerces():
    normalized = common.normalize_settings(
        {
            "theme_index": 999,
            "brightness": -5,
            "contrast": 80,
            "status_service_enabled": "off",
            "clock_blink_colon": "yes",
        }
    )

    assert normalized["theme_index"] == len(common.THEMES) - 1
    assert normalized["brightness"] == 0
    assert normalized["contrast"] == 63
    assert normalized["status_service_enabled"] is False
    assert normalized["clock_blink_colon"] is True


def test_load_settings_missing_file_returns_defaults(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    assert common.load_settings(str(missing)) == common.default_settings()


def test_load_settings_invalid_json_returns_defaults(tmp_path):
    settings_path = tmp_path / "invalid.json"
    settings_path.write_text("{not-json", encoding="utf-8")
    assert common.load_settings(str(settings_path)) == common.default_settings()


def test_load_settings_normalizes_values(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "theme_index": -5,
                "brightness": 150,
                "contrast": -9,
                "status_service_enabled": "1",
                "clock_blink_colon": "0",
            }
        ),
        encoding="utf-8",
    )

    loaded = common.load_settings(str(settings_path))
    assert loaded["theme_index"] == 0
    assert loaded["brightness"] == 100
    assert loaded["contrast"] == 0
    assert loaded["status_service_enabled"] is True
    assert loaded["clock_blink_colon"] is False


def test_save_settings_creates_parent_and_normalizes(tmp_path):
    settings_path = tmp_path / "nested" / "settings.json"
    common.save_settings(
        {
            "theme_index": 100,
            "brightness": -100,
            "contrast": 70,
            "status_service_enabled": "false",
            "clock_blink_colon": "true",
        },
        str(settings_path),
    )

    saved = json.loads(settings_path.read_text(encoding="utf-8"))
    assert saved["theme_index"] == len(common.THEMES) - 1
    assert saved["brightness"] == 0
    assert saved["contrast"] == 63
    assert saved["status_service_enabled"] is False
    assert saved["clock_blink_colon"] is True


def test_theme_name_clamps_index():
    assert common.theme_name(-9) == common.THEMES[0][0]
    assert common.theme_name(999) == common.THEMES[-1][0]


def test_apply_display_scales_backlight_and_sets_contrast():
    class FakeBacklight:
        def __init__(self):
            self.rgb_value = None

        def rgb(self, r, g, b):
            self.rgb_value = (r, g, b)

    class FakeLcd:
        def __init__(self):
            self.contrast = None

        def set_contrast(self, value):
            self.contrast = value

    fake_backlight = FakeBacklight()
    fake_lcd = FakeLcd()

    common.apply_display(
        fake_lcd,
        fake_backlight,
        {
            "theme_index": 0,
            "brightness": 50,
            "contrast": 22,
        },
    )

    assert fake_backlight.rgb_value == (0, 48, 80)
    assert fake_lcd.contrast == 22
