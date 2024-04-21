import requests
from bs4 import BeautifulSoup
import datetime
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define a list of URLs to monitor
urls_to_monitor = [
    'https://a.co/d/i5jregO',
    'https://a.co/d/4dp5sYD',
    'https://a.co/d/825Czfk',
    'https://a.co/d/825Czfk',
    'https://a.co/d/2S958F0',
    'https://a.co/d/92G6tGA'
]
# Function to scrape the price from the webpage


def get_item_price():
    l = []
    o = {}

    headers = {"accept-language": "en-US,en;q=0.9", "accept-encoding": "gzip, deflate, br",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Use appropriate HTML tags and attributes to locate the item's price
        price_element = soup.find(
            "span", {"class": "a-price"}).find("span")
        if price_element:
            return price_element.text.strip()
        else:
            price_element = soup.find(
                'span', {'class': 'js-de-PriceAmount'})
            if price_element:
                return price_element.text.strip()
            else:
                price_element = soup.find(
                    'span', {'itemprop': 'price'})
                if price_element:
                    return price_element.text.strip()
    return None

# Function to log the price to a CSV file with the date


def log_price(url, price):
    today = datetime.date.today()
    data_to_write = []

    with open('price_log.csv', 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        data_by_url = {row[0]: row for row in csv_reader}

    if url not in data_by_url or data_by_url[url][2] != price:
        # URL doesn't exist or the price has changed, add/update the entry
        data_by_url[url] = [url, str(today), price]
        data_to_write = list(data_by_url.values())
    else:
        # URL is new, add it as a new entry
        data_to_write = [[url, str(today), price]]
        # Write the updated data to the CSV file
    with open('price_log.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(data_to_write)
# Function to read CSV data into a dictionary


def read_csv_data():
    data_by_url = {}
    with open('price_log.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if len(row) >= 3:  # Ensure the row has URL, Date, and Price columns
                url, date, price = row
                data_by_url[url] = {"Date": date, "Price": price}
    return data_by_url

# Function to send an email notification


def send_email(subject, message):
    # Replace with your email server settings and credentials
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'dailypricecheckv1@gmail.com'
    smtp_password = 'wprw rjjx gyag iutz'
    sender_email = 'dailypricecheckv1@gmail.com'
    recipient_email = 'alinail13.ank@gmail.com'

    # Create an SMTP connection
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    server.sendmail(sender_email, recipient_email, msg.as_string())

    # Close the SMTP server connection
    server.quit()


if __name__ == "__main__":
    today = datetime.date.today()
    print(today)
    for url in urls_to_monitor:
        price = get_item_price()

        if price:
            # Check if the price has changed
            data_by_url = read_csv_data()
            if url in data_by_url:
                yesterday_price = data_by_url[url]["Price"]
                if price != yesterday_price:
                    subject = "Price Change Alert"
                    message = f"The price has changed from {yesterday_price} to {price}. Go to {url}"
                    send_email(subject, message)
                    log_price(url, price)
                    print(url + " Price changed." + yesterday_price +
                          " to " + price + " Email should have sent.")
                else:
                    print(url + " " + yesterday_price + " = " +
                          price + " >>> No change detected.")
            else:
                log_price(url, price)

        else:
            print("Price not found on the webpage")
