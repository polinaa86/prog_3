# MIME associations: модуль и тесты pytest

Модуль `mimeapps.py` содержит три функции: `read_associations`, `merge_associations`, `write_associations`.

Файл `test_mimeapps.py` содержит тест-план и параметризованные тесты с временными файлами через `tmp_path`.

## Запуск

```bash
python -m pip install pytest
python -m pytest -v
```

Тесты проверяют чтение, объединение, запись, порядок секций, приоритет приложений, обработку пустых значений и неизменность входных словарей.

Для сдачи опубликуйте файлы в публичном репозитории GitHub, GitFlic, GitLab или GitVerse и отправьте ссылку на него.
