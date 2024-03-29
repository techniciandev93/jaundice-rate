# Фильтр желтушных новостей

[TODO. Опишите проект, схему работы]

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. Туда же помещен код для сайта ИНОСМИ.РУ: `adapters/inosmi_ru.py`.

В перспективе можно создать универсальный адаптер, подходящий для всех сайтов, но его разработка будет сложной и потребует дополнительных времени и сил.

# Как установить

Вам понадобится Python версии 3.10 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

# Как запустить

```python3
python server.py
```

# Как использовать
В параметрах запроса необходимо передать список url со статьями. Кол-во url в одном запросе не больше 10. Пример запроса:

```
http://127.0.0.1:8080/?urls=https://inosmi.ru/social/20190718/245490620.html,https://inosmi.ru/social/20190718/245490620.html,https://inosmi.ru/politic/20190718/245488830.html,https://inosmi.ru/social/20190718/245490620.html,https://inosmi.ru/politic/20190718/245487867.html,https://inosmi.ru/military/20190718/245490081.html
```

Пример ответа:

```
{
  "status": "OK",
  "url": "https://inosmi.ru/social/20190718/245490620.html",
  "score": 0.19,
  "words_count": 533
}
```

# Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/), тестами покрыты фрагменты кода сложные в отладке: text_tools.py и адаптеры. Команды для запуска тестов:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest text_tools.py
```

```
python -m pytest server.py
```

# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
