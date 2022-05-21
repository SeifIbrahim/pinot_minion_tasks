"""
Module responsible for starting and ending selenium based chrome and viewing the video
"""


from returns.result import Result, Success, Failure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

import time
from typing import List, Optional

ADDBLOCK_PATH = r"/mnt/l/Users/nectostr/PycharmProjects/pinot_minion_tasks/extensions/chrome_extension"
STATSFORNERDS_PATH = r"/mnt/l/Users/nectostr/PycharmProjects/pinot_minion_tasks/extensions/5.1.9.1_0"

def extract_qualities(text: str) -> List[int]:
    """
    Extracts numbers from specific youtube window menu text
    :param text: string with options from youtube menu
    :return: parsed numeric list
    """
    # Because of how youtube quality menu created
    lines = text.split("\n")[1:-1]

    nums = [int(s[:s.find("p")]) for s in lines]
    return nums

def find_closest(options: List[int], goal: int) -> int:
    """
    Accepts unsorted list of options and fins the index of closest to the goal option
    :param options:
    :param goal:
    :return: index of closest option
    """
    sorted_options = sorted(options)
    for ind, opt in enumerate(sorted_options):
        if opt >= goal:
            if ind > 0 and (goal - sorted_options[ind - 1] < opt - goal):
                return options.index(sorted_options[ind - 1])
            else:
                return options.index(opt)
    return options.index(opt)

def select_quality(driver: webdriver.Chrome, quality: int) -> None:
    settings = driver.find_element(By.CLASS_NAME,
                                   "ytp-settings-button")  # .find_elements_by_class_name("ytp-settings-button")
    settings.click()
    menu = driver.find_elements(By.CLASS_NAME, 'ytp-menuitem')
    menu[3].click()
    quality_menu = driver.find_element(By.CLASS_NAME, 'ytp-quality-menu')
    options = extract_qualities(quality_menu.text)
    index_to_select = find_closest(options, quality) + 1  # Because we cutted first "go back to menu" option
    menu = driver.find_elements(By.CLASS_NAME, 'ytp-menuitem')
    menu[index_to_select].click()


def watch(url: str, how_long: Optional[int] = 100,
          quality: Optional[int] = None) -> Result[str, str]:
    """
    Function that completes the task of:
    1. Starting the chrome from selenium
    2. Adding the extensions to chrome (on start)
      2.1. AddBlock extension to avoid advertisement
      2.2. JS extension to collect StatsForNerds
    3. Stops Chrome by timeout
    :param url: valid http/s youtube url to video
    :param how_long: seconds, for timeout of video viewing. None for "till the end of video"
    :param quality: None for auto, int ~240-1024 for specific quality selection
    :return: 1 for success

    P.s.:
    1. Better to check parameters such as
            url_patterns = [r"^https?://www.youtube.com/watch?.*",
                            r"https?://youtu.be/.*"]
            for pattern in url_patterns:
                if re.fullmatch(pattern, url):
                    break
            else:
                return Failure("Url does not much youtube video url")
    2. Better to make sure numeric how_long < video length
    (use selenium to get video length from video player text option)
    3. Move everything in relevant Try-except blocks,
    where we catch Base Exception and return failure with relevant text
    Why didn't I done that all? Roman asked me to make simple short code for prepared people
    """

    display = Display(visible=0, size=(800, 600))
    display.start()

    options = Options()

    # For unpacked extension
    options.add_argument("--load-extension=" + STATSFORNERDS_PATH)
    options.add_argument("--load-extension=" + ADDBLOCK_PATH) # path to folder

    # or press space part
    options.add_argument("--autoplay-policy=no-user-gesture-required")

    driver = webdriver.Chrome(service=Service(), options=options)
    time.sleep(2)

    driver.get(url)

    video = driver.find_element(By.ID, 'movie_player')

    if not (quality is None):
        select_quality(driver, quality)

    #video.send_keys(Keys.SPACE)  # hits space for start if option not availible

    if how_long is None:
        player_status = 1 # Suppose video playing now
        while player_status != 0: # While not stopped - see docs
            time.sleep(2) # Random 2s constant not to check to freq
            player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
        how = "End of video"
    else:
        time.sleep(how_long)
        video.send_keys(Keys.SPACE)
        how = "Time limit"

    driver.close()

    return Success(how)


if __name__ == '__main__':
    print(watch("https://www.youtube.com/watch?v=ZzwWWut_ibU", 100, None))
