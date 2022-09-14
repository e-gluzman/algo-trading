from bs4 import BeautifulSoup
import requests
import html5lib
import datetime
import pandas as pd

def get_wsj_urls(start_date: str = '2018-01-01'):

    today = pd.to_datetime('today')

    #start = pd.to_datetime('2020-01-01')
    #start = pd.to_datetime('2022-06-01')
    #start = pd.to_datetime('2018-01-01')
    start = pd.to_datetime(start_date)

    iter_date = start

    base_url = 'https://www.wsj.com/news/archive/'

    urls = []
    dates = []

    # add 0 day date here. 
    #while iter_date.date() != (today + datetime.timedelta(days=1)).date():
    while iter_date.date() != (today).date():

        iter_date = iter_date + datetime.timedelta(days=1)

        year = str(iter_date.date().year)

        month = str(iter_date.date().month)

        if len(month) == 1:
            month = '0' + month

        day = str(iter_date.date().day)

        if len(day) == 1:
            day = '0' + day

        url = base_url + year + '/' + month + '/' + day

        urls.append(url)
        dates.append(iter_date.date())

    return urls, dates

def get_wsj_webpage_content(webpage):

    soup = BeautifulSoup(webpage.content, 'html.parser')
    a = soup.find_all('a')
    art = soup.find_all('article')

    time = []
    subjects = []
    headlines = []
    headline_links = []
    

    for i in art:

        if i.find_all('span')[0]:
            subject = i.find_all('span')[0].get_text()
        else:
            subject = None

        if i.find_all('span')[1]:
            headline = i.find_all('span')[1].get_text()
        else:
            subject = None
        
        subjects.append(subject)
        headlines.append(headline)

        a = i.find_all('a')
        count = 0
        max = len(a) - 1
        link_search = 'not found'
        while (link_search == 'not found') & (count <= max):
            link = a[count].get('href')
            if 'articles' in link:
                link_search = 'complete'
            count += 1
        
        if link_search == 'not found':
            link = None

        #if link not in headline_links:
        headline_links.append(link)

    return time, subjects, headlines, headline_links

def scrape_wsj_archive(start_date: str = '2018-01-01'):

    urls, dates = get_wsj_urls(start_date)

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    dates_list = []
    time = []
    page = []
    page_url = []
    subjects = [] 
    headlines = [] 
    headline_links = []

    for u in range(0,len(urls)):
        
        url = urls[u]
        date = dates[u]
        webpage = requests.get(url, headers=headers)
        soup = BeautifulSoup(webpage.content, 'html.parser')
        
        npages_str = soup.select('span[class*="WSJTheme--pagepicker-total"]')[0].get_text()
        npages = [int(char) for char in npages_str if char.isdigit()]

        t, s, h, hl = get_wsj_webpage_content(webpage)
        time += t
        subjects += s
        headlines += h
        headline_links += hl
        page += [1] * len(h)
        page_url += [url] * len(h)
        dates_list += [date] * len(h)

        for p in range(2, npages[0] + 1):
            subpage_url = url + '?page=' + str(p)
            webpage = requests.get(subpage_url, headers=headers)
            if webpage.status_code == 200:
                t, s, h, hl = get_wsj_webpage_content(webpage)
                time += t
                subjects += s
                headlines += h
                headline_links += hl
                page += [p] * len(h)
                page_url += [subpage_url] * len(h)
                dates_list += [date] * len(h)

    result = pd.DataFrame({
        'date': dates_list,
        #'time': time,
        # 'page': page,
        # 'page_url': page_url,
        'subject': subjects,
        'headline': headlines,
        'headline_link': headline_links
    })

    return result

result = scrape_wsj_archive(start_date = '2022-09-01')

print(result.head(10))

# save results

# your_path = '/Users/gluzman/Desktop/Code/financial-market-forecast'
# path = your_path + '/data/wsj_sept.csv'

# result.to_csv(path)