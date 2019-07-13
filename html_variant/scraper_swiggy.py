import json
import csv
import datetime
# import jsonpickle

import bs4

file_path = "swiggy_raw.html"
file_string = ''

with open(file_path, 'r') as fp:
    file_string = fp.read()

soup = bs4.BeautifulSoup(file_string, "html.parser")
inner_div_contents = soup.find('div')
full_order_divs = inner_div_contents.find_all("div", {"class": "_3xMk0"})

# ? Data structure - Swiggy
# Restaurant Name - String
# Area - String
# Order ID - Int
# Date - Date
# Items - [ ]
# Total paid - Int

# for order_div in full_order_divs:
latest_order_div = full_order_divs[0]
restaurant_name = latest_order_div.find("div", {"class": "_3h4gz"}).text
restaurant_area = latest_order_div.find("div", {"class": "_2haEe"}).text
order_id_and_date = latest_order_div.find("div", {"class": "_2uT6l"}).text

order_id = order_id_and_date.split('|')[0].split('#')[1]
unformatted_date = order_id_and_date.split('|')[1].strip()


formatted_date = datetime.datetime.strptime(
    unformatted_date,
    '%a, %b %d, %I:%M %p')  # Thu, Jul 11, 01:26 PM
