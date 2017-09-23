from bs4 import BeautifulSoup
import requests
from scrape03online import get_doctor_links
from pprint import pprint

u = "http://03online.com"
p = requests.get(u)

doc_info = get_doctor_links(p.text)

pprint(doc_info)
