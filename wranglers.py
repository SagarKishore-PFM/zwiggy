import csv
import json


def basic_wrangler(label, orders):
    # * csv headers
    # * order_id, label, res_name, num_of_items, item_cost_total,\
    # * other_costs_total, discount_total, bill_cost, datetime

    with open(
            f'{label.lower()}_basic_data.csv',
            mode='w',
            newline='') as csv_file:
        fieldnames = [
            'order_id', 'label', 'res_name', 'num_of_items', 'item_cost_total',
            'other_costs_total', 'discount_total', 'bill_cost', 'datetime']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for order in orders:
            order_data = order['order']
            writer.writerow(
                {
                    'order_id': order_data['order_id'],
                    'label': label,
                    'res_name': order_data['restaurant_name'],
                    'num_of_items': order_data['number_of_items'],
                    'item_cost_total': round(order_data['total_cost'] - order_data['other_costs']['total_cost'] + order_data['promos_and_tips']['total_discount'], 2),
                    'other_costs_total': round(order_data['other_costs']['total_cost'], 2),
                    'discount_total': round(-1 * order_data['promos_and_tips']['total_discount'], 2),
                    'bill_cost': round(order_data['total_cost'], 2),
                    'datetime': order_data['datetime']
                }
            )


swiggy_data_path = 'swiggy_data.json'
zomato_data_path = 'zomato_data.json'

# required_data_path = swiggy_data_path
required_data_path = zomato_data_path

with open(required_data_path, 'r', encoding='utf-8') as fp:
    json_data = json.load(fp)

label = json_data['label']
orders = json_data['orders']

if required_data_path == swiggy_data_path:
    save_path = 'swiggy_test_data.csv'
if required_data_path == zomato_data_path:
    save_path = 'zomato_test_data.csv'

basic_wrangler(label, orders)
