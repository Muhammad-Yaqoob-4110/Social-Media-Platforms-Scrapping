import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, SessionNotCreatedException
import time
import pandas as pd

comments_container_css = "div.css-13revos-DivCommentListContainer"
comment_containers_css = "div.css-1mf23fd-DivContentContainer"
username_anchor_css = "a.css-fx1avz-StyledLink-StyledUserLinkName"
comment_text_css = ".css-xm2h10-PCommentText"

def scrape_commenters(post_url: str):
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    print("Getting Post URL .....\n")
    driver.get(post_url)
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, comments_container_css)))
    driver.execute_script("document.querySelector('video').pause();")
    previous_comment_count = 0
    current_comment_count = -1

    print("Loading comments .....\n")
    while previous_comment_count != current_comment_count:
        previous_comment_count = current_comment_count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            wait.until(
                lambda d: d.find_element(By.CSS_SELECTOR, comments_container_css)
                .get_attribute('childElementCount') != previous_comment_count
            )
        except TimeoutException:
            print("No new comments loaded within the timeout period.")
            break

        except StaleElementReferenceException:
            continue

        except SessionNotCreatedException:
            print("Session not created.")
            break

        except Exception as e:
            print(e)
            break

        comments_container = driver.find_element(By.CSS_SELECTOR, comments_container_css)
        current_comment_count = comments_container.get_attribute('childElementCount')
        print(f"Loaded {current_comment_count} comments.")

        if previous_comment_count == current_comment_count:
            print("Reached the end of the comments section.")
            break


    comment_containers = driver.find_elements(By.CSS_SELECTOR, comment_containers_css)
    print(f"Found {len(comment_containers)} comment containers.\n")
    comment_data = []
    print(f"Writing data to file .....\n")
    for container in comment_containers:
        creator_label = container.find_elements(By.CSS_SELECTOR, "span.css-6eutxn-SpanIdentity")
        if not creator_label:
            username_anchor = container.find_element(By.CSS_SELECTOR, username_anchor_css)
            username = username_anchor.get_attribute('href').split('/')[-1][1:]
            comment = container.find_element(By.CSS_SELECTOR, comment_text_css).text
            comment_data.append({"commenter_name": username, "comment_text": comment})
    driver.quit()

    df = pd.DataFrame(comment_data)
    df.to_csv('tiktok_comments.csv', index=False)

scrape_commenters('https://www.tiktok.com/@geonews/video/7393733794173439250')