import os

from bs4 import BeautifulSoup
# import pandas as pd
import json
# from pprint import pprint
import requests
import re
import time

the_url = "http://03online.com"


class Question:
    def __init__(self, sp, answers):
        question_block = sp.select("#content_main > div.divide-block.question-block")[0]
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
        ans_block = sp.select('#answers_block')[0]
        ans = ans_block.select('div.answer-block.doctor-block > div.body.right')
        if len(ans) > 0 and answers > 0:
            try:
                self.answer = {
                    'doctor_name': ans[0].select('div.header > a')[0].text,
                    'doctor': ans[0].select('div.header > span.doctor')[0].text,
                    'date': ans[0].select('div.header > span.date')[0].text,
                    'content': ans[0].select('div.content')[0].text,
                }
            except:
                self.answer = {}
        else:
            self.answer = {}


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
        time.sleep(timeout)
    return question_links


def get_n_question_blocks_per_doc(doc_name, values, blocks=3, timeout=0.1):
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
    doc_link = values['link']
    questions = []
    doc = doc_link.lstrip(the_url + '/news/').split('/')[0]
    filename = "data/{}.json".format(doc)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    for b in range(1, min(values['max_page'], blocks) + 1):
        u = doc_link.replace('/1-', '/{}-'.format(b))
        print(u)
        rqb = requests.get(u)  # request questions block page
        # print(rq.ok)
        try:
            sq = BeautifulSoup(rqb.text, 'html.parser')
            question_block_links = get_question_links_per_page(sq)
            ans = int(sq.select('div[class="question-short-block"]')[0]
                      .select('div.extra > div.comments > div.value')[0].text)
            print("question block links:", question_block_links)
            for ql in question_block_links:
                # print("processing link:", ql)
                req = requests.get(ql)
                try:
                    the_question = scrape_question(req.text, ans)
                    questions.append(the_question)
                except Exception as e:
                    print("Failed to process", ql)
                    print("Exception", e)
            time.sleep(timeout)
        except Exception as e:
            print("Unable to process question block. ", e)
    print('Saving {} questions to file {}'.format(len(questions), filename))
    with open(filename, 'w') as f:
        json.dump(questions, f)
    return questions


def scrape_question(page_text, ans):
    """
        Scrape the questions from specific question page
        :param page_text: str
        :return: Question
        """

    sq = BeautifulSoup(page_text, 'html.parser')
    question = Question(sq, ans)

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
        q = get_n_question_blocks_per_doc(d, v, blocks=800)

    # TODO: add throttling
