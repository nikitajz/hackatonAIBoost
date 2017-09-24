from bs4 import BeautifulSoup
# import pandas as pd
import json
from pprint import pprint
import requests
import re
import time
from scrape03online import get_n_question_blocks_per_doc, scrape_question

the_url = "http://03online.com"

doctor_link = 'http://03online.com/news/allergolog/1-0-23'

doc = {
            'link': doctor_link,
            'max_page': 457,
            'question_links': [],
            'questions': []
        }

get_n_question_blocks_per_doc('allergolog', doc, blocks=457)


## questions/answers per doc
# ql = 'http://03online.com/news/nizkiy_ig_e_no_vysypaniya_ne_prohodyat/2017-9-22-337601'
# questions_per_block = []
# req = requests.get(ql)
# # q = scrape_question(req.text)
# soup = BeautifulSoup(req.text, 'html.parser')
# ans = soup.select('#answers_block > div.answer-block.doctor-block > div.body.right')[0]
# # print(q)
# print(ans)
#
# answer = {
#                 'doctor_name': ans.select('div.header > a')[0].text,
#                 'doctor': ans.select('div.header > span.doctor')[0].text,
#                 'date': ans.select('div.header > span.date')[0].text,
#                 'content': ans.select('div.content')[0].text,
# }
#
# print()
# pprint(answer)

# req = requests.get(doctor_link)
# soup = BeautifulSoup(req.text, 'html.parser')
#
# el = soup.select('div[class="question-short-block"]')[0].select('div.extra > div.comments > div.value')[0].text
#
# print(el)

