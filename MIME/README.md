# MIME associations module

Модуль Python для чтения, объединения и записи файлов `mimeapps.list`.

## Функции

- `read_associations(path)` — чтение файла в словарь секций и MIME-типов.
- `merge_associations(old, new)` — объединение с приоритетом `new` без изменения аргументов.
- `write_associations(associations, path)` — запись непустых секций в требуемом порядке.

Используется только стандартная библиотека Python.

## Запуск тестов

```bash
python -m unittest -v
```

## Пример

```python
from mime_associations import read_associations, merge_associations, write_associations

old = read_associations("mimeapps.list")
new = {"Default Applications": {"text/plain": ["org.gnome.TextEditor.desktop"]}}
merged = merge_associations(old, new)
write_associations(merged, "mimeapps_updated.list")
```

Файл создаётся без завершающей точки с запятой в строках ассоциаций, как требует задание.
