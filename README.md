# Сравниваем вакансии программистов

Приложение позволяет оценить количество вакансий и среднюю зарплату разработчиков для популярных языков программирования: JavaScript, Java, Python, Ruby, PHP, C++, C#, C, Go.
Данные о вакансиях собираются с сайтов [SuperJob](https://www.superjob.ru/) и [HH](https://hh.ru/).

## Как установить

Скачайте код
```
https://github.com/user-name-art/week4_api_vacancies.git
```
При необходимости создайте виртуальное окружение. Например: 
```
python -m venv .venv
``` 
Установите зависимости:
```
pip install -r requirements.txt
```

## Как запустить

Для работы понадобится файл **.env** (смотри **.env.template** для примера). 
* **SJ_TOKEN** содержит Secret key, который можно получить после регистрации на [api.superjob.ru](https://api.superjob.ru/).

Запустите скрипт:
```
python3 main.py
```
Выполнение может занимать около минуты. Результат будет выглядеть примерно так:
![222](https://github.com/user-name-art/week4_api_vacancies/assets/112713337/8de9824c-da88-4f0c-a611-409c5c427b43)


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
