import time
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from telegram_bot import TelegramHandler


class InfoCar(TelegramHandler):
    def __init__(self, token: str, id: str, login: str, password: str) -> None:
        super().__init__(token, id)
        self.username = login if (login != None) else input("Provide Info-car username:")
        self.password = password if (password != None) else input("Provide Info-car password:")

        self.today = 0
        options = Options()
        options.add_argument("--incognitoff")
        options.add_argument("--log-level=WARNING")
        # options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.dates = list()

    def login(self) -> None:
        self.driver.get("https://info-car.pl/oauth2/login")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "logo"))
        )
        username = self.driver.find_element(By.CLASS_NAME, "login-input")
        password = self.driver.find_element(By.CLASS_NAME, "password-input")

        username.send_keys("maaciejjarosz@gmail.com")
        password.send_keys(self.password + Keys.ENTER)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, "cookiescript_accept"))
        )

        self.driver.find_element(By.ID, "cookiescript_accept").click()

    def check_term(self) -> None:
        try:
            self.driver.get("https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//span[text() = "Egzamin na prawo jazdy (PKK)"]'))
            )

            self.driver.find_element(By.XPATH, '//span[text() = "Egzamin na prawo jazdy (PKK)"]').click()

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "ng-star-inserted")]'))
            )
            province = self.driver.find_element(By.XPATH, '//input[@id = "province"]')
            province.send_keys("Małopolskie" + Keys.ENTER)

            organization = self.driver.find_element(By.XPATH, '//input[@id = "organization"]')
            organization.send_keys("MORD Kraków" + Keys.ENTER)

            category = self.driver.find_element(By.XPATH, '//input[@id = "category-select"]')
            category.send_keys("A" + Keys.ENTER)

            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@type = "submit"]'))
            )
            accept_btn = self.driver.find_element(By.XPATH, '//button[@type = "submit"]')

            self.driver.execute_script("arguments[0].scrollIntoView();", accept_btn)

            time.sleep(2)
            accept_btn.click()

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="row radio-datepick"]'))
            )
            self.driver.find_element(By.XPATH, '//input[@aria-label = "PRACTICE"]').click()

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//section[@class="container container-accordion"]'))
            )

            self.dates = self.driver.find_elements(By.XPATH, '//*[contains(@class, "m-0")]')
        except StaleElementReferenceException as e:
            print("Cannot login, problem on the server side.")
        except NoSuchElementException as e:
            print("One of the element coundn't be found.")
        except Exception as e:
            print(f"Exception Occured")

    async def verify_dates(self, number_of_days: int = 7) -> None:
        try:
            today = datetime.today().strftime('%d.%m.%y')
            next_week = (datetime.today() + timedelta(days=number_of_days))
            new_dates_available = False
            if (self.today != today):
                print(f"Today is: {today}")
                print(f"next week is: {next_week.strftime('%d.%m.%y')}")
                self.today = today

            for x in range(len(self.dates)):
                # print(self.dates[x].text)

                date = f"{self.dates[x].text.split()[1]}.{next_week.strftime('%y')}"
                a = datetime.strptime(date, "%d.%m.%y")
                b = next_week
                if (a < b):
                    await self.bot.send_message(chat_id=self.bot_channel_id, text=f'New date available: {self.dates[x].text}')

                    print(f"TERMIN!!!!!!!!!!! {self.dates[x].text}")
                    new_dates_available = True

            if not new_dates_available:
                print(f"No new dates available, first term is: {self.dates[0].text}")
        except Exception as e:
            print(e)

    def __del__(self) -> None:
        self.driver.quit()
