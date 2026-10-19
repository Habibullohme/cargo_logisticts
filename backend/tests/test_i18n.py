from app.i18n import t


def test_known_key():
    assert t("health.db_ok") == "Baza bilan aloqa bor"


def test_unknown_key_returns_key():
    assert t("no.such.key") == "no.such.key"


def test_unknown_locale_falls_back_to_uzbek_latin():
    assert t("health.db_ok", locale="xx") == "Baza bilan aloqa bor"
