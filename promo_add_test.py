# -*- coding: utf-8 -*-
import unittest
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PromoblocksTest(unittest.TestCase):

    #delete old screenshot artifacts. Not in setUp method because it`s run for every test
    os.system('find -iname \*.png -delete')

    def setUp(self):
        
        self.base_url = 'http://nsk.%s/' % os.getenv('SITE')
        self.ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
        self.PROMO_LIST_DESC = 'terminal/admin/site/terminal/tpromoblocks/list?filter%5B_sort_order%5D=DESC&filter%5B_sort_by%5D=id&filter%5B_page%5D=1'
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.TEST_DATA = {'title': 'AutoTestPromoAdd',
                          'filename': os.getenv('WORKSPACE') + '/terminal.swf',
                          'stubfilename': os.getenv('WORKSPACE') + '/terminal-stub.gif',
                          'ga_mask': """_gaq.push(['_trackEvent', 'Banners', 'Center', '{0}']); ga('send', 'event', 'Banners', 'Center', '{0}');""",
                         }


    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""

        self.driver.get('%slogout' % self.base_url)
        self.driver.close()
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    def is_element_present(self, how, what, timeout = 10, screen = True):
        """ Поиск элемента по локатору

            По умолчанию таймаут 10 секунд, не влияет на скорость выполнения теста
            если элемент найден, если нет - ждет его появления 10 сек
            
            Параметры:
               how - метод поиска
               what - локатор
            Методы - атрибуты класса By:
             |  CLASS_NAME = 'class name'
             |  
             |  CSS_SELECTOR = 'css selector'
             |  
             |  ID = 'id'
             |  
             |  LINK_TEXT = 'link text'
             |  
             |  NAME = 'name'
             |  
             |  PARTIAL_LINK_TEXT = 'partial link text'
             |  
             |  TAG_NAME = 'tag name'
             |  
             |  XPATH = 'xpath'
                                             """
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((how, what)))
        except:
            print u'Элемент не найден'
            print 'URL: ', self.driver.current_url
            print u'Метод поиска: ', how
            print u'Локатор: ', what
            if screen:
                screen_name = '%d.png' % int(time.time())
                self.driver.get_screenshot_as_file(screen_name)
                print u'Скриншот страницы: ', self.ARTSOURCE + screen_name
            raise Exception('ElementNotPresent')

    def test_promoblocks(self):

        driver = self.driver
        element = self.is_element_present
        TEST_DATA = self.TEST_DATA
        cnt = 0

        #login
        driver.get('%slogin' % self.base_url)
        element(By.ID, 'username').send_keys(os.getenv('AUTH'))
        element(By.ID, 'password').send_keys(os.getenv('AUTHPASS'))
        element(By.CLASS_NAME, 'btn-primary').click()
        time.sleep(10)

        #add new script insert
        driver.get(self.base_url + self.PROMO_LIST_DESC)
        element(By.LINK_TEXT, u"Добавить новый").click()

        #select activity
        element(By.CSS_SELECTOR, 'input[id*="_active"]').click()

        #add title
        element(By.CSS_SELECTOR, 'textarea[id*="_title"]').clear()
        element(By.CSS_SELECTOR, 'textarea[id*="_title"]').send_keys(TEST_DATA['title'])

        #select type of content
        Select(element(By.CSS_SELECTOR, 'select[id*="_contentType"]')).select_by_visible_text(u"Flash-анимация")

        #add swf file and stubfile
        element(By.CSS_SELECTOR, 'input[id*="_filename"]').send_keys(TEST_DATA['filename'])
        element(By.CSS_SELECTOR, 'input[id*="_stubfilename"]').send_keys(TEST_DATA['stubfilename'])

        #change priority
        element(By.CSS_SELECTOR, 'input[id*="_priority"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_priority"]').send_keys('9999999')

        #add description
        element(By.CSS_SELECTOR, 'input[id*="_description"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_description"]').send_keys('test made promo')

        #add promos link
        element(By.CSS_SELECTOR, 'input[id*="_link"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_link"]').send_keys('/test/')

        #name to analitics string
        element(By.CSS_SELECTOR, 'input[id*="_gaType"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_gaType"]').send_keys('test-promo')

        #select nsk
        element(By.CSS_SELECTOR, 'input[id*="_cities_1"]').click()

        #show weight
        element(By.CSS_SELECTOR, 'input[id*="_weight"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_weight"]').send_keys('1000000')

        #берем текущую дату
        current = time.strftime("%Y/%m/%d").split('/')

        #show settings from current day
        Select(element(By.CSS_SELECTOR, 'select[id*="_startDate_year"]')).select_by_visible_text(current[0])
        Select(element(By.CSS_SELECTOR, 'select[id*="_startDate_month"]')).select_by_visible_text(current[1])
        Select(element(By.CSS_SELECTOR, 'select[id*="_startDate_day"]')).select_by_visible_text(current[2])

        #show settings to last day of a current year
        Select(element(By.CSS_SELECTOR, 'select[id*="_stopDate_year"]')).select_by_visible_text(current[0])
        Select(element(By.CSS_SELECTOR, 'select[id*="_stopDate_month"]')).select_by_visible_text('12')
        Select(element(By.CSS_SELECTOR, 'select[id*="_stopDate_day"]')).select_by_visible_text('31')

        #save settings and check successed insert to db
        driver.find_element_by_name("btn_create_and_list").click()        

        #save settings
        driver.get(self.base_url + self.PROMO_LIST_DESC)

        #try find a db insert
        element(By.LINK_TEXT, TEST_DATA['title'])  #without try because we break a test if element is not created
        td_list = element(By.TAG_NAME, 'tbody').\
                  find_element_by_tag_name('tr').\
                  find_elements_by_tag_name('td')
        filename_path = 'http://static1.terminal.ru/' + td_list[7].find_element_by_tag_name('a').text
        stub_filename_path = 'http://static1.terminal.ru/' + td_list[8].find_element_by_tag_name('a').text         

        #chesk promo in public
        driver.get(self.base_url)
        driver.refresh()
        
        first_promo = element(By.CLASS_NAME, 'segNaviLine0').find_element_by_tag_name('a')
        href = first_promo.get_attribute('href')
        onclick = first_promo.get_attribute('onclick')
        obj = first_promo.find_element_by_tag_name('object')
        obj_data = obj.get_attribute('data')
        param_value = obj.find_elements_by_tag_name('param')[2].get_attribute('value')
        img_src = obj.find_element_by_tag_name('img').get_attribute('src')

        if href != self.base_url + 'test/':
            cnt += 1
            print 'Ссылка не соответствует'
            print 'Необходимо: ', self.base_url + 'test/'
            print 'На странице: ', href
            print '*'*80

        if onclick != TEST_DATA['ga_mask'].format('test-promo'):
            cnt += 1
            print 'onclick не соответствует'
            print 'Необходимо: ', TEST_DATA['ga_mask'].format('test-promo')
            print 'На странице: ', onclick
            print '*'*80

        if obj_data != filename_path or param_value != filename_path:
            cnt += 1
            print 'Ссылки на файл не соответствуют'
            print 'Необходимая: ', filename_path
            print 'Ссылка в <object>: ', obj_data
            print 'Ссылка в <param>: ', param_value
            print '*'*80

        if img_src != stub_filename_path:
            cnt += 1
            print 'Ссылка на заглушку не соответствует'
            print 'Необходимая: ', stub_filename_path
            print 'Ссылка в <img>: ', img_src
            print '*'*80
            

        #delete setting
        driver.get(self.base_url + self.PROMO_LIST_DESC)
        element(By.LINK_TEXT, TEST_DATA['title']).click()
        element(By.LINK_TEXT, u'Удалить').click()
        element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        driver.get(self.base_url + self.PROMO_LIST_DESC)

        try:
            print 'Проверка удаления элемента'
            element(By.LINK_TEXT, TEST_DATA['title'], screen=False)
            cnt += 1
            print 'Промоблок не удалился'
            driver.get_screenshot_as_file('remove_error.png')
            print u'Скриншот страницы: ', self.ARTSOURCE + 'remove_error.png'
            print '*'*80
        except:
            pass
        


        assert cnt == 0, ('Errors: %s' % cnt)
