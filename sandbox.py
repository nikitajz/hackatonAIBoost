from bs4 import BeautifulSoup
import requests

# u = "http://03online.com/news/bespokoit_allergiya/2017-9-22-337414"
u = "http://03online.com/news/nizkiy_ig_e_no_vysypaniya_ne_prohodyat/2017-9-22-337601"
rm = requests.get(u)
soup = BeautifulSoup(rm.text, 'html.parser')

# question_title = soup.select("#content_main > div.divide-block.question-block")[0]
question_raw = soup.select("#content_main > div.divide-block.question-block")[0]


# print(question_block)
# question_content = soup.select("#content_main > div.divide-block.question-block > div.question-content > div.content.question > div.extra-info.top")

class Question:
    def __init__(self, question_block):
        self.title = question_block.select('h1[class="title"]')[0].text
        content = question_block.select('div.question-content > div.content.question')[0]
        # extra_info = question_block.select('div.question-content > div.extra-info.bottom')[0]
        self.name = content.select('div.extra-info.top > div')[0].contents[1].strip(" ")
        self.sex = content.select('div.extra-info.top > div')[1].contents[1].strip(" ")
        self.age = content.select('div.extra-info.top > div')[2].contents[1].strip(" ")
        self.chronic_condition = content.select('div.extra-info.top > div')[3].select('i')[0].text
        self.text = content.select('div.text')[0].text
        self.cat_title = question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[0].text
        self.cat_link = question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[0]['href']
        self.published_date = question_block.select('div.question-content > div.extra-info.bottom > div.cat > a')[1]['href'].lstrip('/news/')


question = Question(question_raw)

print(question.title)
# print(question.content)
# print(question.extra_info)
# print(question.extra_info)
print(question.name)
print(question.sex)
print(question.age)
print(question.chronic_condition)
print(question.text)
print(question.cat_title)
print(question.cat_link)
print(question.published_date)


