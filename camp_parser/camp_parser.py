from tqdm import tqdm
import pandas as pd
import requests
import bs4 as bs
import re
from multiprocessing import Pool

class camphub_parser:

    def __init__(self, source=None):
        self.source = source
        self.info = self.all_camp_info()
        # request and pass the source to BeautifulSoup

    def get_soup(self, url):
        r = requests.get(url)
        soup = bs.BeautifulSoup(r.text, 'html.parser')
        return soup

    def all_camp_article(self, link):
        # get all article tag
        articles = self.get_soup(link).find_all('article')
        return articles
    
    def camp_info(self, article):
        # get title and link and description
        def get_title_link_desc(article):
            title = article.find('a')['title']
            link = article.find('a')['href']
            desc = article.find('p').text
            return title, link, desc

        # get all information in camp
        def get_info(inside_pages):
            def description_stripper(text):
                text = text.replace(u'\u200b', '')
                text = re.sub(r'\n', '', text)
                return text
            full_description = [description_stripper(x.text) for x in inside_pages.find('div', {'class':'entry-content'}).find_all('p')]
            full_description = ' '.join(full_description)

            info = []
            for i in inside_pages.find_all('h4'):
                info.append(i.get_text(separator=" ").strip())
            mapping = {'type':info[0], 'organize_date':info[1], 'register_deadline':info[2], 'max_paticipants':info[3], 'costs':info[4], 'paticipants_requirements':info[5], 'organizer':info[6], 'full_description':full_description}
            return mapping
        
        def info_parser(article):
            title, link, small_description = get_title_link_desc(article)
            info = {'title':title, 'link':link, 'small_description':small_description}
            inside_pages = self.get_soup(link)
            info.update(get_info(inside_pages))
            return info
        
        return info_parser(article)

    # get all article camp info
    def all_camp_info(self, source=None):
        if source is None:
            source = self.source
        articles = self.all_camp_article(source)
        camp_info_list = []
        for article in articles:
            camp_info_list.append(self.camp_info(article))
        return camp_info_list

    #  Turn camp into dataframe
    def camp2df(self, info):
        dataf = pd.DataFrame(columns=['title', 'link', 'small_description', 'type', 'organize_date', 'register_deadline', 'max_paticipants', 'costs', 'paticipants_requirements', 'organizer', 'full_description'])
        dataf['title'] = [x['title'] for x in info]
        dataf['link'] = [x['link'] for x in info]
        dataf['small_description'] = [x['small_description'] for x in info]
        dataf['type'] = [x['type'] for x in info]
        dataf['organize_date'] = [x['organize_date'] for x in info]
        dataf['register_deadline'] = [x['register_deadline'] for x in info]
        dataf['max_paticipants'] = [x['max_paticipants'] for x in info]
        dataf['costs'] = [x['costs'] for x in info]
        dataf['paticipants_requirements'] = [x['paticipants_requirements'] for x in info]
        dataf['organizer'] = [x['organizer'] for x in info]
        dataf['full_description'] = [x['full_description'] for x in info]
        return dataf

    def all_info(self, data):
        source, i = data
        return self.all_camp_info(f'{source}/page/{i}/')
    
    # fetch many pages at once
    def page_fetching(self, source, pages, workers = 1):
        dataframe = self.camp2df(self.all_camp_info(source))
        if workers != 1:
            index = [(source, i) for i in range(2, pages + 2)]
            with Pool(workers) as p:
                result = list(tqdm(p.imap(self.all_info, index), total = pages))
            
            for value in result:
                dataframe = dataframe.append(value, ignore_index=True)
        else:
            for i in tqdm(range(2, pages + 2)):
                dataframe = dataframe.append(self.camp2df(self.all_camp_info(f'{source}/page/{i}/')), ignore_index=True)
        
        return dataframe.reset_index(drop=True)
