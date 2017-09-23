import os

import errno
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


def get_doctor_links(page, timeout=0.1):
    """
    For the page scrape link for each doctor and max_page.
    :param page: request.text
    :return:
    """
    print("Collecting basic info per doctor")
    soup = BeautifulSoup(page, 'html.parser')
    doc = {}
    for a_tag in soup.find_all('a', href=re.compile("/news/\w+/1-0-[0-9]+")):
        # print(a)
        link = the_url + a_tag['href']
        rp = requests.get(link)  # request question blocks page
        sp = BeautifulSoup(rp.text, 'html.parser')
        max_page = get_max_question_block_page(sp.select('div[class="paging-block"]')[0].select('a[href]'))
        # doctors[a_tag.text] = {
        doc[a_tag.text] = {
            'link': link,
            'max_page': max_page,
            'question_links': [],
            'questions': []
            }
        time.sleep(timeout)
    return doc


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


def get_question_links(link, max_page, timeout=0.1):
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
            questions_per_block = []
            time.sleep(timeout)
        return question_links


def get_n_question_blocks_per_doc(doc_link, blocks=3, timeout=0.1):
    """Given the doctor page, extract all questions' links.
    For example:
        link: http://03online.com/news/allergolog/1-0-23
        max_page: 457
    :param doc_link[string]
    :param blocks[int]
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

    # question_links = []
    questions = []
    doc = doc_link.lstrip(the_url + '/news/').split('/')[0]
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    filename = "data/{}.json".format(doc)
    for b in range(1, blocks + 1):
        u = doc_link.replace('/1-', '/{}-'.format(b))
        print(u)
        rqb = requests.get(u)  # request questions block page
        # print(rq.ok)
        sq = BeautifulSoup(rqb.text, 'html.parser')
        question_block_links = get_question_links_per_page(sq)
        print("question block links:", question_block_links)
        questions_per_block = []
        for ql in question_block_links:
            print("processing link:", ql)
            req = requests.get(ql)
            questions_per_block.append(scrape_question(req.text))
        questions.append(questions_per_block)
        time.sleep(timeout)
    with open(filename, 'w') as f:
        json.dump(questions, f)
    return questions


def scrape_question(page_text):
        """
        Scrape the questions from specific question page
        :param page_text: str
        :return: Question
        """

        sq = BeautifulSoup(page_text, 'html.parser')
        question_raw = sq.select("#content_main > div.divide-block.question-block")[0]
        question = Question(question_raw)
        # TODO: add answers:
        # answers = question_block.select('#answers_block > div.answer-block.doctor-block')[0]
        # if len(answers.find_all('div', {'class': 'answer-block doctor-block'})) > 0:
        #     ans = answers.find_all('div', {'class': 'answer-block doctor-block'})
        # else:
        #     ans = []

        return question.__dict__


if __name__ == "__main__":

    s = requests.Session()
    s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        })

    rm = requests.get(the_url)

    soup = BeautifulSoup(rm.text, 'html.parser')

    # print(soup.prettify())

    doctors = get_doctor_links(rm.text)

    with open('doctors_info.json', 'w') as outfile:
        json.dump(doctors, outfile)
    for d, v in doctors.items():  # replace below line when testing completed
        get_n_question_blocks_per_doc(v['link'], blocks = 100)

    # collect questions urls from block pages
    # for d, v in d1.items(): # purely for testing
    # for d, v in doctors.items():  # replace below line when testing completed
    #     v['question_links'] = get_question_links(v['link'], v['max_page'])
    #     doctors[d] = v

    # for d, v in doctors.items():
    #     questions = []
    #     question_links = get_question_links(v['link'], v['max_page'])
    #     for l in v['question_links']:
    #         print("Collection questions for page", l)
    #         rq = requests.get(l)
    #         scrape_question(rq.text)
    #         questions.extend(q)
    #         v['questions'] = questions
    #         doctors[d] = v
    #         time.sleep(0.1)
    #     doc_name = v['link'].lstrip(the_url + '/news/').split('/')[0]
    #     with open(doc_name + '.json', 'w') as outfile:
    #         json.dump(v, outfile)

    # pprint(doctors['Аллерголог'])

    # TODO: add throttling
    # TODO: add export to file (json?)

