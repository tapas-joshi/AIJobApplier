import os
import random
import time
import json
from loguru import logger
from selenium import webdriver

chromeProfilePath = os.path.join(os.getcwd(), "chrome_profile", "linkedin_profile")


def remove_duplicates_from_answers_json_file(file_path):
    try:
        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            logger.info(f"Reading data from {file_path}")
            json_data = json.load(file)

        # Create a set to keep track of seen (type, question) pairs
        seen = set()
        unique_entries = []

        for entry in json_data:
            try:
                # Create a tuple of the type and question
                identifier = (entry['type'], entry['question'])

                # If this pair hasn't been seen before, add it to the unique list and mark it as seen
                if identifier not in seen:
                    seen.add(identifier)
                    unique_entries.append(entry)
                else:
                    logger.debug(f"Duplicate found and skipped: {identifier}")

            except KeyError as e:
                logger.error(f"Missing expected key in entry: {e}. Entry: {entry}")

        # Write the updated unique entries back to the same file
        with open(file_path, 'w') as file:
            logger.info(f"Writing unique entries back to {file_path}")
            json.dump(unique_entries, file, indent=4)

        logger.info("Duplicate removal process completed successfully.")

    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}. Error: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file: {file_path}. Error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")


def ensure_chrome_profile():
    profile_dir = os.path.dirname(chromeProfilePath)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    if not os.path.exists(chromeProfilePath):
        os.makedirs(chromeProfilePath)
    return chromeProfilePath


def is_scrollable(element):
    scroll_height = element.get_attribute("scrollHeight")
    client_height = element.get_attribute("clientHeight")
    return int(scroll_height) > int(client_height)


def scroll_slow(driver, scrollable_element, start=0, end=3600, step=100, reverse=False):
    if reverse:
        start, end = end, start
        step = -step
    if step == 0:
        raise ValueError("Step cannot be zero.")
    script_scroll_to = "arguments[0].scrollTop = arguments[1];"
    try:
        if scrollable_element.is_displayed():
            if not is_scrollable(scrollable_element):
                print("The element is not scrollable.")
                return
            if (step > 0 and start >= end) or (step < 0 and start <= end):
                print("No scrolling will occur due to incorrect start/end values.")
                return
            for position in range(start, end, step):
                try:
                    driver.execute_script(script_scroll_to, scrollable_element, position)
                except Exception as e:
                    print(f"Error during scrolling: {e}")
                time.sleep(random.uniform(1.0, 2.6))
            driver.execute_script(script_scroll_to, scrollable_element, end)
            time.sleep(1)
        else:
            print("The element is not visible.")
    except Exception as e:
        print(f"Exception occurred: {e}")


def chromeBrowserOptions():
    ensure_chrome_profile()
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Avvia il browser a schermo intero
    options.add_argument("--no-sandbox")  # Disabilita la sandboxing per migliorare le prestazioni
    options.add_argument("--disable-dev-shm-usage")  # Utilizza una directory temporanea per la memoria condivisa
    options.add_argument("--ignore-certificate-errors")  # Ignora gli errori dei certificati SSL
    options.add_argument("--disable-extensions")  # Disabilita le estensioni del browser
    options.add_argument("--disable-gpu")  # Disabilita l'accelerazione GPU
    options.add_argument("window-size=1200x800")  # Imposta la dimensione della finestra del browser
    options.add_argument("--disable-background-timer-throttling")  # Disabilita il throttling dei timer in background
    options.add_argument("--disable-backgrounding-occluded-windows")  # Disabilita la sospensione delle finestre occluse
    options.add_argument("--disable-translate")  # Disabilita il traduttore automatico
    options.add_argument("--disable-popup-blocking")  # Disabilita il blocco dei popup
    options.add_argument("--no-first-run")  # Disabilita la configurazione iniziale del browser
    options.add_argument("--no-default-browser-check")  # Disabilita il controllo del browser predefinito
    options.add_argument("--disable-logging")  # Disabilita il logging
    options.add_argument("--disable-autofill")  # Disabilita l'autocompletamento dei moduli
    options.add_argument("--disable-plugins")  # Disabilita i plugin del browser
    options.add_argument("--disable-animations")  # Disabilita le animazioni
    options.add_argument("--disable-cache")  # Disabilita la cache 
    options.add_experimental_option("excludeSwitches", ["enable-automation",
                                                        "enable-logging"])  # Esclude switch della modalità automatica e logging

    # Preferenze per contenuti
    prefs = {
        "profile.default_content_setting_values.images": 2,  # Disabilita il caricamento delle immagini
        "profile.managed_default_content_settings.stylesheets": 2,  # Disabilita il caricamento dei fogli di stile
    }
    options.add_experimental_option("prefs", prefs)

    if len(chromeProfilePath) > 0:
        initialPath = os.path.dirname(chromeProfilePath)
        profileDir = os.path.basename(chromeProfilePath)
        options.add_argument('--user-data-dir=' + initialPath)
        options.add_argument("--profile-directory=" + profileDir)
    else:
        options.add_argument("--incognito")

    return options


def printred(text):
    # Codice colore ANSI per il rosso
    RED = "\033[91m"
    RESET = "\033[0m"
    # Stampa il testo in rosso
    print(f"{RED}{text}{RESET}")


def printyellow(text):
    # Codice colore ANSI per il giallo
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    # Stampa il testo in giallo
    print(f"{YELLOW}{text}{RESET}")
