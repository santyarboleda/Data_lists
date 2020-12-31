from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd


URL = "https://www.funcionpublica.gov.co/web/sigep/hojas-de-vida"


class Utilities:
    def __init__(self):
        pass

    def browser_settings(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("window-size=1920x1480")
        chrome_options.add_argument("disable-dev-shm-usage")

        driver = webdriver.Chrome(
            chrome_options=chrome_options,
            executable_path=ChromeDriverManager().install(),
        )
        return driver

    def pep_scraping(self, list_, driver, search_field, search_button):
        list_ = list(map(lambda x: x.lower(), list_))
        people = {}
        driver.get(URL)
        for i in list_:
            try:
                iframe = WebDriverWait(driver, 0.00001).until(
                    ec.element_to_be_clickable(
                        (
                            By.ID,
                            "_com_liferay_iframe_web_portlet_IFramePortlet_INSTANCE_MJDhjBvQWqsM_iframe",
                        )
                    )
                )
                driver.switch_to.frame(iframe)

                driver.find_element_by_name(search_field).clear()
                driver.find_element_by_name(search_field).send_keys(i)
                driver.find_element_by_name(search_button).click()
                WebDriverWait(driver, 0.00001).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, "columna-datos"))
                )
                # time.sleep(2)
            except:
                pass
            finally:
                elements = driver.find_elements_by_class_name("columna-datos")
                found = []
                for k in elements:
                    for j in k.find_elements_by_tag_name("span"):
                        found.append(j.text.lower())
                        break
                driver.switch_to.parent_frame()
                people[i] = found
        driver.close()
        return people

    # function to create dataframe with people and entities data
    def fill_people_data(self, people, list_):
        count = []
        for i in people:
            print(i, "--", len(people[i]))
            count.append(len(people[i]))

        df_pep = pd.DataFrame(list_)
        df_pep = df_pep.rename(columns={df_pep.columns[0]: "nombre"})
        df_pep["cantidad"] = count
        df_pep["cantidad"] = df_pep["cantidad"].astype(int)
        return df_pep

    def read_data(self, list_):
        search_field = "query"
        search_button = "find"

        # initializing browser
        driver = self.browser_settings()

        # scrap page result
        people = self.pep_scraping(list_, driver, search_field, search_button)

        # fill dataframe
        df_pep = self.fill_people_data(people, list_)

        return df_pep