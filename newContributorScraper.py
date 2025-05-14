from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import argparse
import os
import sys
import time
import urllib.parse


logged_into_phab = False

def main():
    OUTPUT_FILE_NAME = 'New_Contributors.txt'

    url, timer = validate_args()

    driver = webdriver.Firefox()
    driver.get(url)

    login_bugzilla(driver, timer)

    driver.get(url)
    lst = go_through_bug_list(driver)

    fp = open(OUTPUT_FILE_NAME, 'w')
    fp.write('New Contributors\n')
    fp.write('-' * 83 + '\n')

    for ele in lst:
        fp.write(f'{ele[0]}\n{ele[1]}\n\n')

    fp.close()

    driver.close()

# Validate args using argparse
def validate_args():
    # Default wait time of 20 seconds for Duo, if not specified as an arg
    DEFAULT_TIMER = 20

    parser = argparse.ArgumentParser()
    # url is a required argument
    parser.add_argument('url', type=url_type, help='The URL of recently resolved bugs. Link should be from the latest bi-weekly meeting.')
    # Optional arguments
    parser.add_argument('--timer', type=timer_type, default=DEFAULT_TIMER, help='The number of seconds of wait for Duo notification. Default is 20.')
    args = parser.parse_args()

    return args.url, args.timer


# For validating the url
def url_type(url):
    try:
        parsed_url = urllib.parse.urlparse(url)

        if not bool(parsed_url.netloc) or not bool(parsed_url.scheme):
            raise argparse.ArgumentError(None, f'Invalid URL found')
        if parsed_url.netloc != 'bugzilla.mozilla.org':
            raise argparse.ArgumentError(None, f'URL should be from bugzilla.mozilla.org')
        if 'quicksearch' not in parsed_url.query:
            raise argparse.ArgumentError(None, f'Missing list of bugs in url')

        return url

    except argparse.ArgumentError as e:
        print(f'argparse.ArgumentError: {e}')
        sys.exit(1)

# For validating the timer arg
def timer_type(seconds):
    try:
        converted_to_int = int(seconds)

        if not isinstance(converted_to_int, int):
            raise argparse.ArgumentError(None, f'Invalid timer found')
        if converted_to_int < 1:
            raise argparse.ArgumentError(None, f'Timer cannot be zero or negative seconds')
        
        return converted_to_int


    except argparse.ArgumentError as e:
        print(f'argparse.ArgumentError: {e}')
        sys.exit(1)


def login_bugzilla(driver, timer):
    driver.find_element(By.ID, 'login_link_top').click()

    login_username = driver.find_element(By.ID, 'Bugzilla_login_top')
    login_password = driver.find_element(By.ID, 'Bugzilla_password_top')

    # Need to set these environment variables to your username and password
    login_username.send_keys(os.getenv('BUGZILLA_USERNAME'))
    login_password.send_keys(os.getenv('BUGZILLA_PASSWORD'))

    login_button = driver.find_element(By.ID, 'log_in_top')
    login_button.click()

    # Waits for the Duo iframe to load and for you to accept the push notification.
    time.sleep(timer)

# Logging into Phabricator is easy here. Just clicks a few buttons the first time visiting.
def login_to_phab(driver):
    driver.find_element(By.CLASS_NAME, 'phabricator-core-login-button').click()

    btn = driver.find_elements(By.TAG_NAME, 'button')[3]
    print('button: ', btn.get_attribute('class'))
    btn.click()

    driver.find_element(By.NAME, 'submit').click()
    global logged_into_phab
    logged_into_phab = True


# Loops through the bug list and checks if the bug was assigned to a
# "New User" and if that was their first patch
def go_through_bug_list(driver):
    bug_list = get_bug_list_links(driver)

    new_user_list = []
    for link in bug_list:
        driver.get(link)

        bug_id = link.split('=')[1]

        username, title = get_username(driver)

        if not username:
            return

        new_user = check_if_new_user(driver, username, title, bug_id)
        if new_user:
            new_user_list.append([new_user, link])
    return new_user_list


# Creates a list of the bug links
def get_bug_list_links(driver):
    ele = driver.find_element(By.LINK_TEXT, "Assignee")

    ele.click()

    bug_list = []

    bugs = driver.find_elements(By.TAG_NAME, "tr")
    for bug in bugs:
        hasId = bug.get_attribute('id')
        if hasId:
            link = bug.find_element(By.TAG_NAME, "a")
            bug_list.append(link.get_attribute('href'))

    return bug_list


# Returns the username of the user and 'username + email'.
# The title is needed for checking that the attachment in bugzilla
# is from the correct user
def get_username(driver):
    ele = driver.find_element(By.ID, 'field-value-assigned_to')
    title = ele.find_element(By.CLASS_NAME, 'show_usermenu').get_attribute('title')
    index = title.find('<')
    if index < 0:
        index = title.find('@')
        return title[:index].strip(), title

    return title[:index].strip(), title


# Checks that the bug is the first non abandoned revision in the users
# phabricator profile
def check_if_first_patch(driver, title, bug_id):
    try:
        attachments = driver.find_elements(By.CLASS_NAME, 'attach-patch')
        for att in attachments:
            user = att.find_element(By.CLASS_NAME, 'show_usermenu').get_attribute('title')
            print(user, title)
            if user == title:
                phab_link = att.find_element(By.CLASS_NAME, 'attach-desc').find_element(By.TAG_NAME, 'a').get_attribute('href')
                print(phab_link)
                driver.get(phab_link)

                print('Logged in:', logged_into_phab)
                if not logged_into_phab:
                    login_to_phab(driver)
                
                driver.find_element(By.CLASS_NAME, 'phui-link-person').click()

                buttons = driver.find_elements(By.CLASS_NAME, 'phui-list-item-href')
                for button in buttons:
                    if 'revisions' in button.get_attribute('href'):
                        button.click()
                        break

                patches = driver.find_elements(By.CLASS_NAME, 'phui-oi-table-row')
                print('number of patches', len(patches))
                for i in range(len(patches) - 1, -1, -1):
                    print(i)
                    p = patches[i]
                    try:
                        p.find_element(By.CLASS_NAME, 'fa-plane')
                        continue
                    except:
                        patch_name = p.find_element(By.CLASS_NAME, 'phui-oi-link').get_attribute('innerHTML')
                        if bug_id in patch_name[:15]:
                            return '#'
                        return ''
                return ''
        return 'No Attachment. Check manually\n'

    except Exception as e:
        print(f'Exception: {e}')
        return ''


# Checks if the "New User" is on the users comment
def check_if_new_user(driver, username, title, bug_id):
    changes = driver.find_elements(By.CLASS_NAME, 'change-set')

    for change in changes:
        try:
            ele = change.find_element(By.PARTIAL_LINK_TEXT, username)
            double_parent = ele.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
            try:
                double_parent.find_element(By.CLASS_NAME, 'new_user')
                short_desc = driver.find_element(By.ID, 'field-value-short_desc').get_attribute('innerHTML')
                star = check_if_first_patch(driver, title, bug_id)
                temp = f'{star} {username}: {short_desc}'
                return temp

            except:
                # print(f'{username} is not a new user')
                return ''

        except:
            # print("Comment not made by assignee")
            continue
    return f'Check manually. No comment from assignee\n {username}'


if __name__ == "__main__":
    main()
