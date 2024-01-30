import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import logging
import yaml
import sys
import time
import random
import undetected_chromedriver as udc

load_dotenv()

sendgrid_on = False
coron_jobs = True

if coron_jobs:
    # logica de cron jobs
    import time
    import atexit

    from apscheduler.schedulers.background import BackgroundScheduler


    def print_date_time():
        print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
        Prenota.run()


    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=print_date_time,

        trigger="interval",
        seconds=1800  # 30 minutos
    )
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


if sendgrid_on:
    # logica de sengrid
    message = Mail(
        from_email="sender@host.dom",
        to_emails="destinatary@host.dom",
        subject="Sending with Twilio SendGrid is Fun",
        html_content='''
            <main>
                <h1>Sistema de alertas de embajada</h1>
                <p>Se ha detectado un cambio en la pagina de la embajada</p>
                <p>Rapido dirijete a <a href="#">este link</a> para reservar un turno</p>
            </main>
        ''',
    )

    try:
        sender = SendGridAPIClient('sendgrid_api_key')
        result = sender.send(message)
        print(result.status_code)
        print(result.body)
        print(result.headers)

    except Exception as e:
        print(e)

    exit(200)

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("/temp/out.log"), logging.StreamHandler(sys.stdout)],
)


class Prenota:
    @staticmethod
    def check_file_exists(file_name):
        file_path = os.path.join(os.getcwd(), file_name)
        return os.path.isfile(file_path)

    @staticmethod
    def load_config(file_path):
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    @staticmethod
    def check_for_dialog(driver):
        try:
            dialog = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            button_inside_dialog = dialog.find_element(
                By.XPATH, "//button[contains(text(),'ok')]"
            )
            button_inside_dialog.click()
            logging.info(
                f"Timestamp: {str(datetime.now())} - Scheduling is not available right now."
            )
            return True
        except NoSuchElementException:
            logging.info(
                f"Timestamp: {str(datetime.now())} - Element WlNotAvailable not found. Start filling the forms."
            )
            return False

    @staticmethod
    def fill_citizenship_form(driver, user_config):
        try:
            driver.get("https://prenotami.esteri.it/Services/Booking/1019")
            time.sleep(6)
            if not Prenota.check_for_dialog(driver):
                logging.critical("ENTRO EN EL FORMULARIO")
                driver.save_screenshot("files/citizenship_form.png")
                '''
                file_location = os.path.join("files/residencia.pdf")
                choose_file = driver.find_elements(By.ID, "File_0")
                choose_file[0].send_keys(file_location)
                privacy_check = driver.find_elements(By.ID, "PrivacyCheck")
                privacy_check[0].click()
                submit = driver.find_elements(By.ID, "btnAvanti")
                submit[0].click()
                with open("files/citizenship_form.html", "w") as f:
                    f.write(driver.page_source)
                return True
                '''


        except Exception as e:
            logging.error(f"NO ENTRO EN LA CIUDADANIA -> {e}")
            return False

    @staticmethod
    def fill_passport_form(driver, user_config):
        try:
            time.sleep(10)
            driver.get("https://prenotami.esteri.it/Services/Booking/1319")
            time.sleep(5)

            if not Prenota.check_for_dialog(driver):
                with open("files/passport_form.html", "w") as f:
                    f.write(driver.page_source)

                q0 = Select(driver.find_element(By.ID, "ddls_0"))
                q0.select_by_visible_text(user_config.get("possess_expired_passport"))

                q1 = Select(driver.find_element(By.ID, "ddls_1"))
                q1.select_by_visible_text(user_config.get("possess_expired_passport"))

                q2 = driver.find_element(By.ID, "DatiAddizionaliPrenotante_2___testo")
                q2.send_keys(user_config.get("total_children"))

                q3 = driver.find_element(By.ID, "DatiAddizionaliPrenotante_3___testo")
                q3.send_keys(user_config.get("full_address"))

                q4 = Select(driver.find_element(By.ID, "ddls_4"))
                q4.select_by_visible_text(user_config.get("marital_status"))

                time.sleep(1)

                file0 = driver.find_element(By.XPATH, '//*[@id="File_0"]')
                file0.send_keys(os.getcwd() + "/files/identidade.pdf")

                time.sleep(1)

                file1 = driver.find_element(By.XPATH, '//*[@id="File_1"]')
                file1.send_keys(os.getcwd() + "/files/residencia.pdf")

                checkBox = driver.find_element(By.ID, "PrivacyCheck")
                checkBox.click()

                form_submit = driver.find_element(By.ID, "btnAvanti")
                form_submit.click()

                return True
        except Exception as e:
            logging.info(f"Exception {e}")
            return False

    @staticmethod
    def run():

        email = "gandolfoignaciounmdp@gmail.com"  # os.getenv("username")
        password = "Prueba123!"  # os.getenv("password")

        print(f"email {email} password {password}")
        user_config = Prenota.load_config("parameters.yaml")
        print(user_config.get("full_address"))
        options = udc.ChromeOptions()
        options.headless = False
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = udc.Chrome(use_subprocess=True, options=options)
        driver.delete_all_cookies()

        try:
            driver.get("https://prenotami.esteri.it/")
            email_box = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "login-email"))
            )
            password_box = driver.find_element(By.ID, "login-password")
            email_box.send_keys(email)
            password_box.send_keys(password)
            time.sleep(4)
            button = driver.find_elements(
                By.XPATH, "//button[contains(@class,'button primary g-recaptcha')]"
            )
            button[0].click()
            logging.info(
                f"Timestamp: {str(datetime.now())} - Successfully logged in."
            )
            driver.save_screenshot("files/login.png")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Exception: {e}")

        for i in range(200):
            random_number = random.randint(1, 5)

            if user_config["request_type"] == "citizenship":
                if Prenota.fill_citizenship_form(driver, user_config):
                    break
            elif user_config["request_type"] == "passport":
                if Prenota.fill_passport_form(driver, user_config):
                    break

            time.sleep(random_number)

        user_input = input(
            f"Timestamp: {str(datetime.now())} - Go ahead and fill manually the rest of the process. "
            f"When finished, type quit to exit the program and close the browser. "
        )
        while True:
            if user_input == "quit":
                driver.quit()
                break


if __name__ == "__main__":
    print("Starting Prenota...")
    Prenota.run()
    while True:  # bucle infinito para que se ejecute siempre y el cronjob no se detenga
        pass
