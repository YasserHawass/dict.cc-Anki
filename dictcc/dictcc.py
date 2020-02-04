# -*- coding: utf-8 -*-
# MOD
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# MOB
import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup
    BeautifulSoup.find_all = BeautifulSoup.findAll

AVAILABLE_LANGUAGES = {
    "en": "english",
    "de": "german",
    "fr": "french",
    "sv": "swedish",
    "es": "spanish",
    "nl": "dutch",
    "bg": "bulgarian",
    "ro": "romanian",
    "it": "italian",
    "pt": "portuguese",
    "ru": "russian"
}


class UnavailableLanguageError(Exception):
    def __str__(self):
        return "Languages have to be in the following list: {}".format(
            ", ".join(AVAILABLE_LANGUAGES.keys()))


class Result(object):
    def __init__(self, from_lang=None, to_lang=None, translation_tuples=None):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.translation_tuples = list(translation_tuples) \
                                  if translation_tuples else []

    @property
    def n_results(self):
        return len(self.translation_tuples)


class Dict(object):
    @classmethod
    def translate(cls, word, from_language, to_language):
        if any(map(lambda l: l.lower() not in AVAILABLE_LANGUAGES.keys(),
                   [from_language, to_language])):
            raise UnavailableLanguageError

        response_body = cls._get_response(word, from_language, to_language)
        result = cls._parse_response(response_body)

        return cls._correct_translation_order(result, word)

    @classmethod
    def _get_response(cls, word, from_language, to_language):
        res = requests.get(
            url="https://" + from_language.lower() + to_language.lower() + ".dict.cc",
            params={"s": word.encode("utf-8")},
            headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'}
        )
        # MOD
        # print(word)
        driver = webdriver.Firefox()
        driver.get("https://" + from_language.lower() + to_language.lower() + ".dict.cc/")
        element1 = driver.find_element_by_id("sinp")
        element1.send_keys(word)
        element1.send_keys(u'\ue007')
        driver.implicitly_wait(4)
        button1 = driver.find_element_by_xpath("//tr[@id='tr1']//td[4]//img[1]")
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(button1,0,0)
        actions.click()
        actions.perform()

        # button1.click()
        # actions.click()

        # calc the button for Ham
        menu1 = driver.find_element_by_class_name("amenu")
        button2 = driver.find_element_by_xpath("//div[@id='overDiv']//input[3]")
        # Dict Name:Code [ele.get_attribute('...')]
        # input[Code], brick, Paragraph[text[Name]]
        # print(help(menu1))
        lista = (i.get_attribute("onclick") for i in menu1.find_elements_by_css_selector("input"))
        list_pc = (i.get_attribute("text") for i in menu1.find_elements_by_css_selector("b"))
        # list_users = (i.get_property("text") for i in menu1.find_elements_by_css_selector(":not(a[style='color:#999']) > a"))
        list_users = (i.get_property("text") for i in menu1.find_elements_by_css_selector('a') if i.get_property("style")["color"] == '' )
        for i in list_users:
            print(i)
        # Press it
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(button2,0,0)
        actions.click()
        actions.perform()
        
        # button1 = driver.find_elements_by_css_selector("table:nth-child(7) tbody:nth-child(1) tr:nth-child(3) td.td7cmr:nth-child(4) > img:nth-child(1)")
        # button1.click()
        # print(button1.location)

        # button1 = driver.find_element_by_css_selector("#tr1 > .td7cmr > img:nth-child(1)")
        # print(button1)
        # button1.click()
        # print(button1)
        # button2 = driver.find_elements_by_css_selector(".inp3:nth-child(7)")
        # button2.click()
        # button = driver.find_element_by_id('tr1')
        # print (button)
        # button.click()
        # MOB
        #print (res.content.decode("utf-8"))
        return res.content.decode("utf-8")

    # Quick and dirty: find javascript arrays for input/output words on response body
    @classmethod
    def _parse_response(cls, response_body):
        soup = BeautifulSoup(response_body, "html.parser")

        suggestions = [tds.find_all("a") for tds in soup.find_all("td", class_="td3nl")]
        if len(suggestions) == 2:
            languages = [lang.string for lang in soup.find_all("td", class_="td2")][:2]
            if len(languages) != 2:
                raise Exception("dict.cc results page layout change, please raise an issue.")

            return Result(
                from_lang=languages[0],
                to_lang=languages[1],
                translation_tuples=zip(
                    [e.string for e in suggestions[0]],
                    [e.string for e in suggestions[1]]
                ),
            )

        translations = [tds.find_all(["a", "var"]) for tds in soup.find_all("td", class_="td7nl", attrs={'dir': "ltr"})]
        if len(translations) >= 2:
            languages = [next(lang.strings) for lang in soup.find_all("td", class_="td2", attrs={'dir': "ltr"})]
            if len(languages) != 2:
                raise Exception("dict.cc results page layout change, please raise an issue.")

            return Result(
                from_lang=languages[0],
                to_lang=languages[1],
                translation_tuples=zip(
                    [" ".join(map(lambda e: " ".join(e.strings), r)) for r in translations[0:-1:2]],
                    [" ".join(map(lambda e: e.string if e.string else "".join(e.strings), r)) for r in translations[1:-1:2]]
                ),
            )

        return Result()

    # Heuristic: left column is the one with more occurrences of the to-be-translated word
    @classmethod
    def _correct_translation_order(cls, result, word):

        if not result.translation_tuples:
            return result

        [from_words, to_words] = zip(*result.translation_tuples)

        return result if from_words.count(word) >= to_words.count(word) \
                      else Result(
                          from_lang=result.to_lang,
                          to_lang=result.from_lang,
                          translation_tuples=zip(to_words, from_words),
                      )


