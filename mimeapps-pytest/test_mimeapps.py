import pytest

from mimeapps import read_associations, merge_associations, write_associations

"""
Тест-план

read_associations:
  1. Чтение каждой из трёх секций и списков приложений по приоритету.
  2. Чтение пустого файла и файла с пустой секцией.
  3. Удаление завершающей точки с запятой и пропуск пустых элементов.
  4. Ошибка FileNotFoundError при отсутствии файла.

merge_associations:
  1. Перезапись совпадающего MIME-типа в одной секции новым значением.
  2. Сохранение MIME-типов, имеющихся только в одном словаре.
  3. Сохранение и объединение разных секций.
  4. Отсутствие изменений исходных словарей и независимость вложенных списков.

write_associations:
  1. Строгий порядок трёх секций независимо от порядка ключей словаря.
  2. Пропуск пустых секций (в том числе всех сразу).
  3. Запись нескольких приложений без завершающей точки с запятой.
  4. Корректное чтение записанного файла (round-trip).
"""


@pytest.mark.parametrize(
    ("section", "mime_type", "applications"),
    [
        ("Default Applications", "text/plain", ["editor.desktop", "other.desktop"]),
        ("Added Associations", "image/png", ["viewer.desktop"]),
        ("Removed Associations", "application/pdf", ["old.desktop"]),
    ],
)
def test_read_each_section(tmp_path, section, mime_type, applications):
    """Читает любую допустимую секцию и сохраняет порядок приложений."""
    path = tmp_path / "mimeapps.list"
    path.write_text(f"[{section}]\n{mime_type}={';'.join(applications)};\n", encoding="utf-8")
    assert read_associations(str(path)) == {section: {mime_type: applications}}


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("", {}),
        ("[Default Applications]\n", {"Default Applications": {}}),
    ],
)
def test_read_empty(tmp_path, content, expected):
    """Корректно обрабатывает пустой файл и пустую секцию."""
    path = tmp_path / "mimeapps.list"
    path.write_text(content, encoding="utf-8")
    assert read_associations(str(path)) == expected


def test_read_ignores_empty_items(tmp_path):
    """Не включает пустые имена приложений в список."""
    path = tmp_path / "mimeapps.list"
    path.write_text("[Default Applications]\ntext/plain=one.desktop;;two.desktop;\n", encoding="utf-8")
    assert read_associations(str(path))["Default Applications"]["text/plain"] == ["one.desktop", "two.desktop"]


def test_read_missing_file(tmp_path):
    """Сообщает об отсутствующем файле."""
    with pytest.raises(FileNotFoundError):
        read_associations(str(tmp_path / "missing.list"))


def test_merge_overwrites_same_mime():
    """Для совпадающего MIME-типа выбирает значение из new."""
    old = {"Default Applications": {"text/plain": ["old.desktop"]}}
    new = {"Default Applications": {"text/plain": ["new.desktop"]}}
    assert merge_associations(old, new) == new


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ({"Default Applications": {"text/plain": ["a.desktop"]}},
         {"Default Applications": {"image/png": ["b.desktop"]}},
         {"Default Applications": {"text/plain": ["a.desktop"], "image/png": ["b.desktop"]}}),
        ({}, {"Added Associations": {"image/png": ["b.desktop"]}},
         {"Added Associations": {"image/png": ["b.desktop"]}}),
        ({"Removed Associations": {"image/png": ["a.desktop"]}}, {},
         {"Removed Associations": {"image/png": ["a.desktop"]}}),
    ],
)
def test_merge_preserves_unique_entries(old, new, expected):
    """Сохраняет записи и секции, встречающиеся только с одной стороны."""
    assert merge_associations(old, new) == expected


def test_merge_different_sections():
    """Не смешивает одинаковые MIME-типы из разных секций."""
    old = {"Default Applications": {"text/plain": ["a.desktop"]}}
    new = {"Removed Associations": {"text/plain": ["b.desktop"]}}
    assert merge_associations(old, new) == {**old, **new}


def test_merge_does_not_mutate_inputs():
    """Не изменяет исходные словари и не разделяет с ними вложенные списки."""
    old = {"Default Applications": {"text/plain": ["a.desktop"]}}
    new = {"Added Associations": {"image/png": ["b.desktop"]}}
    merged = merge_associations(old, new)
    merged["Default Applications"]["text/plain"].append("changed.desktop")
    merged["Added Associations"]["image/png"].append("changed.desktop")
    assert old == {"Default Applications": {"text/plain": ["a.desktop"]}}
    assert new == {"Added Associations": {"image/png": ["b.desktop"]}}


def test_write_section_order(tmp_path):
    """Записывает секции в обязательном порядке, а не в порядке словаря."""
    associations = {
        "Removed Associations": {"image/png": ["r.desktop"]},
        "Added Associations": {"image/png": ["a.desktop"]},
        "Default Applications": {"image/png": ["d.desktop"]},
    }
    path = tmp_path / "mimeapps.list"
    write_associations(associations, str(path))
    content = path.read_text(encoding="utf-8")
    assert content.index("[Default Applications]") < content.index("[Added Associations]") < content.index("[Removed Associations]")


@pytest.mark.parametrize("associations,expected", [
    ({}, ""),
    ({"Default Applications": {}, "Added Associations": {}}, ""),
    ({"Default Applications": {}, "Added Associations": {"image/png": ["a.desktop"]}},
     "[Added Associations]\nimage/png=a.desktop\n"),
])
def test_write_skips_empty_sections(tmp_path, associations, expected):
    """Не записывает заголовки пустых секций."""
    path = tmp_path / "mimeapps.list"
    write_associations(associations, str(path))
    assert path.read_text(encoding="utf-8") == expected


def test_write_no_trailing_semicolon(tmp_path):
    """Разделяет приложения точкой с запятой без завершающего разделителя."""
    path = tmp_path / "mimeapps.list"
    write_associations({"Default Applications": {"text/plain": ["a.desktop", "b.desktop"]}}, str(path))
    assert path.read_text(encoding="utf-8") == "[Default Applications]\ntext/plain=a.desktop;b.desktop\n"


def test_write_read_roundtrip(tmp_path):
    """После записи и чтения сохраняет все MIME-типы и приоритеты."""
    original = {
        "Default Applications": {"text/plain": ["a.desktop", "b.desktop"]},
        "Added Associations": {"image/png": ["viewer.desktop"]},
        "Removed Associations": {"application/pdf": ["old.desktop"]},
    }
    path = tmp_path / "mimeapps.list"
    write_associations(original, str(path))
    assert read_associations(str(path)) == original
