import requests
from bs4 import BeautifulSoup
import smtplib
import time
import argparse
import sys

def check_price(url):

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'lxml')
    #Inspecting the returned HTML, 
    # and realized that Amazon sends a (somewhat malformed?) 
    # HTML that trips the default html.parser, 
    # but using lxml I was able to scrape title just fine.

    # print(soup.prettify())

    title = soup.find(id="productTitle").get_text().strip()
    price = soup.find(id="priceblock_ourprice").get_text()
    previous_price = float(price[1:]) #remove currency

    return title, previous_price

def send_mail(title, url, receiver):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('kdawg4.956@gmail.com', 'ogfmqtfrzavzyibj')
    subject = f"Price decrease for item: {title}"
    body = url

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail('kdawg4.956@gmail.com', 
                    receiver,
                    msg
            )

if __name__ == '__main__':
    argsparser = argparse.ArgumentParser(description='Amazon Price Tracker.')
    argsparser.add_argument('--url', nargs='+', help='Amazon URL of item')
    argsparser.add_argument('--email', nargs=1, help='your email')
    args = argsparser.parse_args(sys.argv[1:])

    title, previous_price = check_price(args.url[0])
    current_price = float('inf')

    while current_price > previous_price:
        _, current_price = check_price(args.url[0])

    send_mail(title,args.url[0], args.email)
