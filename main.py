import requests
import os

from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from=0, salary_to=0):
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    else:
        return (salary_from + salary_to) / 2


def get_table_with_vacancy_statistics(statistics, title):
    statictics_for_print = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, vacancy_statistics in statistics.items():
        vacancy_statistics_by_language = []
        vacancy_statistics_by_language.append(language)

        for vacancy_statistic in vacancy_statistics.values():
            vacancy_statistics_by_language.append(vacancy_statistic)

        statictics_for_print.append(vacancy_statistics_by_language)

    table_instance = AsciiTable(statictics_for_print, title)

    return table_instance.table


def predict_rub_salary_sj(vacancy):
    if not (vacancy['payment_from'] and vacancy['payment_to']):
        return None

    if not vacancy['currency'] == 'rub':
        return None

    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(vacancy):
    if not vacancy['salary']:
        return None

    if not (vacancy['salary']['from'] and vacancy['salary']['to']):
        return None

    if not vacancy['salary']['currency'] == 'RUR':
        return None

    return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def get_vacancy_statistics_sj(headers, languages):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies_per_page = 100
    directory_section_developer = 48
    mocsow_id = 4

    all_vacancies = {}

    for language in languages:
        page = 0
        more = True

        payload = {'count': vacancies_per_page,
                   'catalogues': directory_section_developer,
                   'town': mocsow_id,
                   'page': page,
                   'keywords': f'программист {language}',
        }
        
        vacancies_by_language = []        

        while more:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            
            page_payload = response.json()

            page += 1
            more = page_payload['more']
            payload['page'] = page

            vacancies_by_language += page_payload['objects']
            
        all_vacancies[language] = get_salary_statistics(vacancies_by_language, predict_rub_salary_sj)
    
    return all_vacancies


def get_salary_statistics(vacancies_by_language, predict_rub_salary):
    vacancies_procecced = 0
    sum_salaries = 0
    
    for vacancy in vacancies_by_language:
        vacancy_salary = predict_rub_salary(vacancy)
        if vacancy_salary:
            vacancies_procecced += 1
            sum_salaries += int(vacancy_salary)

    avegare_salary = get_avegare_salary(sum_salaries, vacancies_procecced)
    
    vacancy_stat = {'vacancies_found': len(vacancies_by_language),
                    'vacancies_procecced': vacancies_procecced,
                    'avegare_salary': avegare_salary,
    }

    return vacancy_stat


def get_avegare_salary(sum_salaries, vacancies_procecced):
    avegare_salary = 0
    if vacancies_procecced:
        avegare_salary = int(sum_salaries / (vacancies_procecced))

    return avegare_salary


def get_vacancy_statistics_hh(headers, languages):
    url = 'https://api.hh.ru/vacancies'
    vacancies_per_page = 100
    mocsow_id = 1

    all_vacancies = {}

    for language in languages:
        page = 0
        pages_number = 1

        payload = {'per_page': vacancies_per_page,
                   'area': mocsow_id,
                   'page': page,
                   'text': f'Программист {language}',
        }

        vacancies_by_language = []
        vacancy_stat = {}
        
        while page < pages_number:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            
            page_payload = response.json()
            page += 1
            pages_number = page_payload['pages']

            vacancies_by_language += page_payload['items']

        all_vacancies[language] = get_salary_statistics(vacancies_by_language, predict_rub_salary_hh)

    return all_vacancies


def main():
    load_dotenv()
    languages = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']

    title = 'SuperJob Moscow'
    headers_sj = {'X-Api-App-Id': os.environ['SJ_TOKEN']}

    vacancy_statistics_sj = get_vacancy_statistics_sj(headers_sj, languages)
    print(get_table_with_vacancy_statistics(vacancy_statistics_sj, title))

    print()

    title = 'HH Moscow'
    headers_hh = {'User-Agent': 'VacancyPasres/0.1 (art.gilyazov@mail.ru)'}

    vacancy_statistics_hh = get_vacancy_statistics_hh(headers_hh, languages)
    print(get_table_with_vacancy_statistics(vacancy_statistics_hh, title))


if __name__ == '__main__':
    main()
