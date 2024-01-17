from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Replace 'your_webpage_url' with the actual URL of the Telegram web application
url = 'https://web.telegram.org/k/'

# Replace 'your_chat_id' with the actual chat ID you want to monitor
chat_id = 'your_chat_id'

# Replace 'expected_message' with the message you are waiting for
expected_message = 'Accepteer'

# Replace 'your_reply' with the reply you want to send
your_reply = 'Found the text'

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Open the Telegram web application
driver.get(url)
time.sleep(60)

# Wait for the user to log in manually

# Assuming you're in the chat you want to monitor, let's continuously check for messages
while True:
    try:
        # Find the last message in the chat
        # Find all elements with the CSS selector 'div.message'
        message_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message')

        # Check if there are any elements
        if message_elements:
            # Retrieve the last element
            last_message = message_elements[-1]

        # Extract the text of the last message
        message_text_full = last_message.text
        message_text = message_text_full.split('\n')[0]

        # Check if the expected message is received
        if expected_message.lower() in message_text.lower():
            input_message = driver.find_element(
                By.CSS_SELECTOR, 'div.input-message-input')

            # Type your message into the input element
            input_message.send_keys(your_reply)

            # Press Enter
            input_message.send_keys(Keys.RETURN)

            print(
                f"Expected message received: {expected_message}. Replied with: {your_reply}")
    except Exception as e:
        print(f"Error: {e}")

    # Pause for a short duration to avoid high CPU usage
    time.sleep(5)

# Close the browser window
driver.quit()
