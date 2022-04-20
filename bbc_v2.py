import time
import itertools
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class BBCScraper:
    def __init__(self, chrome_driver_path: str, run_headless: bool = True):
        """
        initializes the BBCScraper class, must provide a path to the chromedriver.exe file,
        and optionally: if you do not want to show the selenium browser; you can set
        run_headless to True when initializing the class.
        :param chrome_driver_path:
        :param run_headless:
        """
        self.run_headless = run_headless
        self.data = None
        self.timer_start = time.time()

        s = Service(chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.headless = self.run_headless

        self.driver = webdriver.Chrome(service=s, options=options)
        self.driver.get("https://www.bbc.com/")

        time.sleep(3)
        self.driver.find_element(By.XPATH, '/html/body/div[9]/div[2]/div[1]/div[2]/div[2]/button[1]/p').click()
        self.driver.find_element(By.XPATH, '//*[@id="bbccookies-continue-button"]/span[2]').click()

    def get_articles_urls(self):
        """
        returns a list with all the article URL's in the first page
        :return:
        """
        articles_lst = self.driver.find_elements(By.CLASS_NAME, "block-link__overlay-link")
        articles_hrefs = [x.get_attribute('href') for x in articles_lst]
        unique_articles = list(set(articles_hrefs))
        return unique_articles

    def scrape_article(self):
        """
        loops through each article-URL, and retrieves:
        the Header/title, and all the text of the article, and will save the text in a list,
        with each paragraph being an element.
        :return:
        """
        unique_articles = BBCScraper.get_articles_urls(self)

        articles = []
        first_article = True

        for article in unique_articles:
            self.driver.execute_script(f'window.open("{article}");')
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(1)
            if first_article:
                time.sleep(5)
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'button.tp-close.tp-active').click()
                except:
                    pass
                first_article = False

            if 'bbc.com/news/live/' in article:

                article_headers = self.driver.find_elements(By.TAG_NAME, "header")
                headers = [x.text for x in article_headers[-20:]]

                article_text = self.driver.find_elements(By.CSS_SELECTOR, 'div.lx-stream-post-body')
                article_text = [x.text for x in article_text]

                image_caption_list1 = self.driver.find_elements(By.XPATH, '//article//figure//figcaption//span[1]')
                image_caption_list1 = [x.text for x in image_caption_list1]

                image_caption_list2 = self.driver.find_elements(By.XPATH, '//article//figure//figcaption//span[2]')
                image_caption_list2 = [x.text for x in image_caption_list2]

                image_copyright_lst = self.driver.find_elements(By.XPATH, '//article//div//div//div//div[2]')
                image_copyright_lst = [x.text for x in image_copyright_lst]

                print(*map(len, [headers, article_text, image_caption_list1, image_caption_list2, image_copyright_lst]))

                for num in range(len(article_text)):
                    for char1, char2, char3 in itertools.zip_longest(image_caption_list1, image_caption_list2,
                                                                     image_copyright_lst, fillvalue=''):
                        article_text[num] = article_text[num].replace(char2, '').replace(char1, '').replace(char3, '')

                if len(headers) == len(article_text):
                    for title, description in zip(headers, article_text):
                        articles.append({'url': article, 'title': title, 'description': description})

            else:
                href = article
                title = self.driver.execute_script("return window.document.title").split(' - BBC')[0]

                article_text = self.driver.find_elements(By.XPATH, "//article//p")
                filtered_text = []
                for paragraph_ in article_text:
                    class_value = paragraph_.get_attribute('class').lower()
                    if class_value is not None and 'paragraph' in class_value:
                        filtered_text.append(paragraph_)

                filtered_text = [x.text for x in filtered_text]
                article_text = [x.text for x in article_text]
                description = filtered_text if len(filtered_text) > 0 else article_text

                print(len(article_text), len(description), href)
                articles.append({'url': href, 'title': title, 'description': description})

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.data = articles

    def exit(self):
        """
        Closes last window, and the driver.
        :return:
        """
        self.driver.close()
        self.driver.quit()
        print(f'Time elapsed: {time.time() - self.timer_start :.2f} sec.')

    def save_data(self, file_path: str, mode: str = 'w'):
        """
        Saves the data to the given path, note that the file type must finish with '.CSV'
        :param data: list
        :param file_path: Path
        :param mode: 'w' for write (replace), and 'a' for appending to an existing file
        :return:
        """
        df = pd.DataFrame(data=self.data)
        df.to_csv(file_path, index=False, mode=mode)


def main():
    bbc_scraper = BBCScraper(chrome_driver_path='chromedriver.exe', run_headless=True)
    bbc_scraper.scrape_article()
    bbc_scraper.save_data(file_path='bbc_data.csv')
    bbc_scraper.exit()
    pass


if __name__ == "__main__":
    main()
var = 'var'
var = 'varr'
var = 'mirarifhasan'
var = 'shner-elmo'
