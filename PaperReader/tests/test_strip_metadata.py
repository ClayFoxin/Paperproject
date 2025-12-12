from paperreader.cleaning.strip_metadata import strip_metadata


def test_strip_metadata_removes_top_level_fields():
    parsed = {
        "metadata": {"title": "A Study", "authors": ["Alice"]},
        "content": {
            "sections": [
                {"heading": "Intro", "text": "This is the intro."},
                {"heading": "Methods", "text": "We did X."},
            ],
            "tables": [
                {"caption": "Table 1", "data": [[1, 2], [3, 4]]}
            ],
            "figures": [
                {"caption": "Figure 1", "description": "A figure"}
            ],
        },
    }

    cleaned = strip_metadata(parsed)

    assert "metadata" not in cleaned
    assert "This is the intro." in cleaned["text"]
    assert "We did X." in cleaned["text"]
    assert cleaned["tables"] == parsed["content"]["tables"]
    assert cleaned["figures"] == parsed["content"]["figures"]
