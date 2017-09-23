from bs4 import BeautifulSoup
# import pandas as pd
import json
from pprint import pprint
import requests
import re
import time

the_url = "http://03online.com"

class Question:
    def __init__(self, question_block):
        self.title = question_block.select('h1[class="title"]')[0].text
        content = question_block.select('div.question-content > div.content.question')[0]
        # extra_info = question_block.select('div.question-content > div.extra-info.bottom')[0]
        self.name = content.select('div.extra-info.top > div')[0].contents[1].strip(" ")
        self.sex = content.select('div.extra-info.top > div')[1].contents[1].strip(" ")
        self.age = content.select('div.extra-info.top > div')[2].contents[1].strip(" ")
        self.chronic_condition = content.select('div.extra-info.top > div')[3].text
        self.text = content.select('div.text')[0].text
        self.cat_title = question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[0].text
        self.cat_link = the_url + \
                        question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[0]['href']
        self.published_date = question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[1][
            'href'].lstrip('/news/')


def get_max_question_block_page(links):
    """
    Given a list of links for a page containing questions, find the last one (they follow the same sequence pattern).

    :param links:
            [<a class="current" href="/news/allergolog/1-0-23"><b>1</b></a>,
             <a href="/news/allergolog/2-0-23">2</a>,
             <a href="/news/allergolog/3-0-23">3</a>,
             ...
            ]
    :return: maxPage[int]
    """

    def only_numerics(page_block_no_string):
        """
        Remove non-numeric characters
        :param page_block_no_string:
        :return: page [int]
        """
        # print(page_block_no_string)
        pb = re.sub(r'\D', '', page_block_no_string)
        return int(pb) if pb.isdigit() else 0

    max_page = 0
    for p in links:
        max_page = max(only_numerics(p.text), max_page)
    return max_page


def get_question_links(link, max_page, timeout=0.25):
        """Given the doctor page, extract all questions' links.
        For example:
            link: http://03online.com/news/allergolog/1-0-23
            max_page: 457
        :param link[string]
        :param max_page[int]
        :param timeout[int] between retries
        :return list[question_link]
        """

        def get_question_links_per_page(tag):
            """
            Given the area tag return list of links for all questions on this page.
            :param tag: soup top level tag
            :return: list of question links on this specific page
            """
            blocks = tag.select('#content_main > div.question-short-block > div.header > a')
            links = [the_url + b['href'] for b in blocks]

            return links

        question_links = []
        for p in range(1, max_page + 1):
            u = link.replace('/1-', '/{}-'.format(p))
            print(u)
            rqb = requests.get(u)  # request questions block page
            # print(rq.ok)
            sq = BeautifulSoup(rqb.text, 'html.parser')
            question_links = get_question_links_per_page(sq)
            time.sleep(timeout)
        return question_links


def scrape_question(page_text):
        """
        Scrape the questions from specific question page
        :param page_text: str
        :return: Question
        """

        sq = BeautifulSoup(page_text, 'html.parser')
        question_raw = sq.select("#content_main > div.divide-block.question-block")[0]
        question = Question(question_raw)
        return question


if __name__ == "__main__":

    s = requests.Session()
    s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        })



    rm = requests.get(the_url)

    soup = BeautifulSoup(rm.text, 'html.parser')

    # print(soup.prettify())

    doctors = dict()

    # collect a link for each doctor/group
    for a in soup.find_all('a', href=re.compile("/news/\w+/1-0-[0-9]+")):
        # print(a)
        doctors[a.text] = {
            'link': the_url + a['href'],
            'max_page': 1,
            'question_links': [],
            'questions': []
            }




    # d1 = {'Аллерголог': {'link': the_url + '/news/allergolog/1-0-23'}}  # for testing only

    # get latest question block page
    # for (d, v) in d1.items():  # purely for testing
    for d, v in doctors.items():  # replace near line when testing completed
        rp = requests.get(v['link'])  # request question blocks page
        sp = BeautifulSoup(rp.text, 'html.parser')
        v['max_page'] = get_max_question_block_page(sp.select('div[class="paging-block"]')[0].select('a[href]'))
        doctors[d] = v
        time.sleep(0.25)






    # collect questions urls from block pages
    # for d, v in d1.items(): # purely for testing
    for d, v in doctors.items():  # replace below line when testing completed
        v['question_links'] = get_question_links(v['link'], v['max_page'])
        doctors[d] = v

    with open('doctors_basic.json', 'w') as outfile:
        json.dump(doctors, outfile)




    for d, v in doctors.items():
        questions = []
        for l in v['question_links']:
            print("Collection questions for page", l)
            rq = requests.get(l)
            scrape_question(rq.text)
            questions.extend(q)
            v['questions'] = questions
            doctors[d] = v
            time.sleep(0.25)


    pprint(doctors['Аллерголог'])

    # TODO: add throttling
    # TODO: add export to file (json?)

    with open('data2.txt', 'w') as outfile:
        json.dump(doctors, outfile)
