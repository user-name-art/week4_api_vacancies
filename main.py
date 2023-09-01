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


def print_to_table(statistics, title):
    statictics_for_print = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, info in statistics.items():
        info_by_language = []
        info_by_language.append(language)

        for value in info.values():
            info_by_language.append(value)

        statictics_for_print.append(info_by_language)

    table_instance = AsciiTable(statictics_for_print, title)

    print(table_instance.table)
    print()


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


def vacancy_statistics_sj(headers, languages):
    url_template = 'https://api.superjob.ru/2.0/vacancies/?count=100&catalogues=48&town=4&keywords=программист'
    count_vacancies = {}

    for language in languages:
        url = f'{url_template} {language}'

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        page = 1
        all_vacancies = response.json()['objects']

        while response.json()['more']:
            response = requests.get(url, headers=headers, params={'page': page})
            response.raise_for_status()
            
            page_payload = response.json()
            page += 1

            all_vacancies += page_payload['objects']
            
        count_vacancies[language] = statistics_processing(all_vacancies, predict_rub_salary_sj)
    
    return count_vacancies


def statistics_processing(all_vacancies, predict_rub_salary):
    vacancy_stat = {}
    vacancies_procecced = 0
    all_salaries = 0
    avegare_salary = 0
    vacancy_stat["vacancies_found"] = len(all_vacancies)
    
    for vacancy in all_vacancies:
        if predict_rub_salary(vacancy):
            vacancies_procecced += 1
            all_salaries += int(predict_rub_salary(vacancy))

    if vacancies_procecced:
        avegare_salary = int(all_salaries / (vacancies_procecced))

    vacancy_stat["vacancies_procecced"] = vacancies_procecced
    vacancy_stat["avegare_salary"] = avegare_salary

    return vacancy_stat


def vacancy_statistics_hh(headers, languages):
    url_template = 'https://api.hh.ru/vacancies?per_page=100&area=1&text=Программист'
    count_vacancies = {}
    for language in languages:
        vacancy_stat = {}
        url = f'{url_template} {language}'

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        vacancy_stat["vacancies_found"] = response.json()["found"]

        page = 1
        pages_number = response.json()['pages']
        all_vacancies = response.json()['items']

        while page < pages_number:
            page_response = requests.get(url, headers=headers, params={'page': page})
            page_response.raise_for_status()
            
            page_payload = page_response.json()
            page += 1

            all_vacancies += page_payload['items']

        count_vacancies[language] = statistics_processing(all_vacancies, predict_rub_salary_hh)

    return count_vacancies


def main():
    load_dotenv()
    languages = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']

    title = 'SuperJob Moscow'
    headers_sj = {'X-Api-App-Id': os.environ["SJ_TOKEN"]}

    sj_vacancies = vacancy_statistics_sj(headers_sj, languages)
    print_to_table(sj_vacancies, title)

    title = 'HH Moscow'
    headers_hh = {'User-Agent': 'VacancyPasres/0.1 (art.gilyazov@mail.ru)'}

    hh_vacancies = vacancy_statistics_hh(headers_hh, languages)
    print_to_table(hh_vacancies, title)


if __name__ == '__main__':
    main()
