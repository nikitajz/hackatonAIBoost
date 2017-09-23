from bs4 import BeautifulSoup
import requests

the_url = "http://03online.com"
u = "http://03online.com/news/allergolog/1-0-23"
rm = requests.get(u)
soup = BeautifulSoup(rm.text, 'html.parser')

def get_question_links_per_page(tag):
    """
    Given the area tag return list of links for all questions on this page.
    :param tag: soup top level tag
    :return: list of question links on this specific page
    """
    blocks = tag.select('#content_main > div.question-short-block > div.header > a')
    links = [the_url + b['href'] for b in blocks]

    return links


# blocks = soup.select('#content_main > div.question-short-block > div.header > a')
# links = [b['href'] for b in blocks]
# print(links)

print(get_question_links_per_page(soup))
