import requests
import bs4
from json_methods import write_data_to_json_file

url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'

headers = {
    'User-Agent': 'Chrome/126.0.0.0 Safari/537.36'
}


# Функция для извлечения города из текста
def extract_city(text):
    if "Москве" in text:
        return "Москва"
    elif "Санкт-Петербурге" in text:
        return "Санкт-Петербург"
    return None


# Функция для проверки ключевых слов
def extract_key_words(text):
    if "Django" in text or "Flask" in text:
        return True
    return False


# Функция для извлечения зарплаты
def extract_salary(same_soup):
    salary_tag = same_soup.find("div", {"data-qa": "vacancy-salary"})
    if salary_tag:
        salary_text = salary_tag.get_text(separator=' ').strip().replace('\xa0', ' ')
        return salary_text
    return "Уровень дохода не указан"


# Функция для извлечения Имени компании
def extract_company_name(same_soup):
    company_tag = same_soup.find("span", class_="vacancy-company-name")
    if company_tag:
        company_name_tag = company_tag.find("span", class_="bloko-header-section-2_lite")
        if company_name_tag:
            return company_name_tag.get_text().strip().replace('\xa0', ' ')
    return "Имя компании не указано"


# Запрос + создание "супа" основной страницы
response = requests.get(url, headers=headers)
html_data = response.text
soup = bs4.BeautifulSoup(html_data, "lxml")

tag_vacancies = soup.find("main", class_="vacancy-serp-content")
vacancies = tag_vacancies.find_all('h2')

parsed_data = []

# Собираем список ссылок на странице
for vacancy in vacancies:
    vac_link = vacancy.find("a")
    link = vac_link["href"]
    # Собираем данные из "супа" вакансии
    vacancy_response = requests.get(link, headers=headers)
    vac_raw = vacancy_response.text
    vacancy_soup = bs4.BeautifulSoup(vac_raw, "lxml")
    # Добываем город
    vacancy_info_tag = vacancy_soup.find("p", class_="vacancy-creation-time-redesigned")
    city = None
    if vacancy_info_tag:
        vacancy_info_text = vacancy_info_tag.get_text(separator=' ')
        city = extract_city(vacancy_info_text)
    # Проверяем описание на ключевые слова
    key_words = vacancy_soup.find("div", class_="vacancy-section")
    key_words_text = key_words.get_text()
    keyword_check = extract_key_words(key_words_text)
    # Извлекаем информацию о зарплате
    salary = extract_salary(vacancy_soup)
    name_company = extract_company_name(vacancy_soup)
    # Добавления собранных данных в список parsed_data если есть ключевые слова в описании:
    if keyword_check:
        parsed_data.append({
            "link": link,
            "city": city,
            "salary": salary,
            "company": name_company
        })

write_data_to_json_file(parsed_data)
