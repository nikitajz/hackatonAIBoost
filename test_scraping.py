from scrape03online import scrape_question
import unittest


class TestClass(unittest.TestCase):
    def test_question_scraping(self):
        print("Reading question page file.")
        with open('resources/allergolog_1-0-23.html') as f:
            page = f.read()

        title = 'Низкий ig e, но высыпания не проходят'
        name = 'Татьяна, Г. Рыбное'
        sex = 'Мужской'
        age = '5 лет'
        chronic_condition = 'не указаны'
        text = 'Здравствуйте, ребенку 5 лет часто высыпания на коже чаще под коленками, на попе, кожа шершавая, после антигистаминных стихает, но последнее время не проходит, и ещё вокруг глаз. Сдали анализы на некоторых паразитов отрицательно, и на общий ig e результат 4,21 ке/л референсные значения 0,00-52,00. Не низкий ли уровень ig e, и почему не стихает дерматит?'
        cat_title = 'Аллерголог'
        cat_link = 'http://03online.com/news/allergolog/1-0-23'
        published_date = '2017-09-22'

        print("Scraping the page")
        q = scrape_question(page)
        self.assertEqual(title, q.title)
        self.assertEqual(name, q.name)
        self.assertEqual(text, q.text)
