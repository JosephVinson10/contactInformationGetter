import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to decode Cloudflare's obfuscated email addresses
def decode_cf_email(cf_email):
    r = int(cf_email[:2], 16)
    email = ''.join([chr(int(cf_email[i:i+2], 16) ^ r) for i in range(2, len(cf_email), 2)])
    return email

# Function to extract data from a single page
def extract_data_from_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {url}: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    data = []

    # Find all article tags with the relevant user information
    articles = soup.find_all('article', class_='user user--default')
    if not articles:
        print(f"No articles found on page {url}")
    for article in articles:
        email_tag = article.find('a', class_='__cf_email__')
        email = 'N/A'
        if email_tag:
            cf_email = email_tag.get('data-cfemail')
            if cf_email:
                email = decode_cf_email(cf_email)

        full_name_tag = article.find('div', class_='user__field-nf-full-name-cp d-flex')
        full_name = 'N/A'
        if full_name_tag:
            full_name_item = full_name_tag.find('div', class_='field__item')
            if full_name_item:
                full_name = full_name_item.text.strip()

        practice_name_tag = article.find('article', class_='node organization organization--default')
        practice_name = 'N/A'
        if practice_name_tag:
            practice_name_item = practice_name_tag.find('span')
            if practice_name_item:
                practice_name = practice_name_item.text.strip()

        address_tag = article.find('div', class_='practice-location__field-location-address')
        city = 'N/A'
        state = 'N/A'
        if address_tag:
            city_tag = address_tag.find('span', class_='locality')
            state_tag = address_tag.find('span', class_='administrative-area')
            if city_tag:
                city = city_tag.text.strip()
            if state_tag:
                state = state_tag.text.strip()

        data.append({
            'Email': email,
            'Full Name': full_name,
            'Practice Name': practice_name,
            'City': city,
            'State': state
        })

    return data

# Function to iterate through pages and collect data
def extract_data(url_template, start_page, end_page):
    all_data = []
    for page_num in range(start_page, end_page + 1):
        url = url_template.format(page_num)
        print(f"Fetching data from {url}")
        page_data = extract_data_from_page(url)
        if not page_data:
            print(f"No data found on page {page_num}")
        all_data.extend(page_data)
        print(f'Extracted data from page {page_num}')
    return all_data

# Function to write data to an Excel spreadsheet
def write_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# Template URL of the website with placeholder for page number
url_template = 'insert url'

# Starting and ending page numbers
start_page = 1
end_page = 796

# Extract data from the website
data = extract_data(url_template, start_page, end_page)
print(data)

# Write data to Excel
write_to_excel(data, 'info.xlsx')
