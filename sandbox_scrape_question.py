from scrape03online import scrape_question, Question
import requests
# from bs4 import BeautifulSoup

u = "http://03online.com/news/otek_nog_vo_vremya_beremennosti/2017-9-20-336840"

r = requests.get(u)
# soup = BeautifulSoup(r.text, 'html.parser')

q = scrape_question(r.text)

print(q)

