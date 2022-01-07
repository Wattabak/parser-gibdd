# stat.gibdd.ru парсер

Инструменты для получения и работы с данными сайта [статистики гибдд](https://stat.gibdd.ru).

## CLI

Пример команды для получения статистики в формате xlsx по региону 90401,
 который находится в федеральном округе 90
```
gibdd verbose -ds 2019-01 -de 2019-02 -R 90 -r 90401
```
   

## DEV

Чтобы использовать комманду `gibdd` необходимо выполнить следующие команды:

```
poetry install
```
