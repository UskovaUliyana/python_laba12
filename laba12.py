from bs4 import BeautifulSoup
import requests

def parse_pepper():
    url = 'https://www.pepper.ru/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    page = requests.get(url, headers=headers)
    print(f'Статус ответа: {page.status_code}')
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('article')
    count = 0
    print('\n' + '=' * 80)
    for article in articles:
        link_elem = article.find('a', href=lambda x: x and ('/deals/' in x or '/coupons/' in x))
        if not link_elem:
            continue
        count += 1
        title = link_elem.get_text(strip=True)
        link = link_elem.get('href')
        if not link.startswith('http'):
            link = 'https://www.pepper.ru' + link
        grade_elem = article.find(
            'span',
            class_=lambda x: x and ('vote' in str(x).lower() or 'temp' in str(x).lower() or 'hot' in str(x).lower())
        )
        grade = grade_elem.get_text(strip=True) if grade_elem else '-'
        print(f'{count}. {title}')
        print(f'   Градусы: {grade}')
        print(f'   Ссылка: {link}')
        print('-' * 80)
    print(f'\nВсего найдено акций: {count}')

if __name__ == '__main__':
    parse_pepper()