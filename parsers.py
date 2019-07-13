# import bs4
import bs4
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)
pp = pp.pprint


def parse_new_zomato(file_path, message_id):
    try:

        with open(file_path, 'r') as fp:
            file_string = fp.read()

        html_string = file_string
        soup = bs4.BeautifulSoup(html_string, "html.parser")
        main_table = soup.table.table
        required_td = main_table.findAll('td', {'style': "text-align: center;vertical-align: top;font-size: 0;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;padding-left: 15px;padding-right: 15px;"})[0]

        # restaurant name

        res_name_td = required_td.find('td', {'style': "padding: 10px 25px 10px 25px;text-align: center;background-color: white;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt; "})
        if res_name_td:
            res_name = res_name_td.div.find('b').text
        # ? Old format fix
        else:
            res_name_td = main_table.find('td', {'style': "-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;font-family: sans-serif;font-size: 14px;line-height: 21px;color: #2d2d2a;text-align: center;"})
            res_name = res_name_td.text.strip()
        # Order ID
        order_id_td = required_td.find('td', {'class': "ta-left smaller-text zdhl5"})
        order_id = order_id_td.text.strip().split(':')[1].strip()

        # Date - Better to get it from email header
        # order_id_td = required_td.find('td', {'class': "ta-left zdhl5 pbot15"})

        # There are three tables with same style and all are relevant

        # * First table
        # * Contains Items, Qty, Price per Qty
        # * User the for loop
        # * first table will always be the items

        # ? DS for items:
        # ? ordered_items = [item, item, ...]
        # ? item = {
        # ?   'name','qty','price_per_qty'
        # ? order_total_price = 0
        order_total_price = 0
        first_table = required_td.findAll('table', {'style': "margin-top: 5px;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-spacing: 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;"})[0]
        items = []
        for table_tr in first_table.findAll('tr'):
            item_td = table_tr.findAll('td')[0]
            total_price = float(table_tr.findAll('td')[1].text.strip()[3:])
            item = {}
            # ? Old format fix -- rsplit instead of split
            split_text = item_td.text.strip().rsplit('(', 1)
            item['name'] = split_text[0].strip()
            qty_and_price_text = split_text[1].split(' x ')
            item['quantity'] = int(qty_and_price_text[0])
            item['price_per_unit'] = float(qty_and_price_text[1].split(')')[0][3:])
            assert \
                item['quantity'] * item['price_per_unit'] == total_price, \
                f"Total doesn't match for {message_id}"

            item['total_price'] = total_price
            order_total_price += total_price

            items.append(item)

        # ? Other Costs Data Structure
        # ? other_costs = {
        # ?     'total', 'split' = list of tuples
        # ? tuples = (cost_name, cost)
        # ?}
        other_costs = {}
        other_costs['total_cost'] = 0
        other_costs['split'] = []

        promos_and_tips = {}
        promos_and_tips['total_discount'] = 0
        promos_and_tips['split'] = []
        promos_and_tips['tip'] = 0

        other_tables = required_td.findAll('table', {'style': "margin-top: 5px;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-spacing: 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;"})[1: ]
        for i, table in enumerate(other_tables):
            if i == 0:  # * then this is charges table
                # second_table = required_td.findAll('table', {'style': "margin-top: 5px;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-spacing: 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;"})[1]
                second_table = table
                for other_costs_tr in second_table.findAll('tr'):
                    other_costs_tds = other_costs_tr.findAll('td')
                    cost_type = other_costs_tds[0].text.strip()
                    # ? Old format fix -- If
                    if other_costs_tds[1].text.strip() == 'FREE':
                        cost_for_given_type = 0
                    else:
                        cost_for_given_type = float(other_costs_tds[1].text.strip()[3:])
                    other_costs['split'].append((cost_type, cost_for_given_type))
                    other_costs['total_cost'] += cost_for_given_type

        # ? Promo discounts and Tip Data Structure
        # ? promos_and_tips = {
        # ? 'total_discount = 0,
        # ? 'split' = list of tuples, each tuple = (promo_name, promo_ammount)
        # ? 'tip' = 0,
        # ? }

            if i == 1:  # * then this is the tips table
                # third_table = required_td.findAll('table', {'style': "margin-top: 5px;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-spacing: 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;"})[2]
                third_table = table
                # third_table_tr = third_table.tr.findAll('td')[0].text.strip()
                if third_table.tr:
                    tip_ammount = float(third_table.tr.findAll('td')[1].text.strip()[3:])
                    promos_and_tips['tip'] = tip_ammount
                else:
                    promos_and_tips['tip'] = 0
        total_bill_and_promo_tables = required_td.findAll(
            'table',
            {
                'style': "-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-spacing: 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;",
                'align': "center",
            }
        )
        if len(total_bill_and_promo_tables) == 2:  # ? Then we have promo table
            promo_table = total_bill_and_promo_tables[0]
            promo_table_trs = promo_table.findAll('tr')
            for promo_table_tr in promo_table_trs:
                promo_table_tr_tds = promo_table_tr.findAll('td')
                promo_name = promo_table_tr_tds[0].text.strip()
                promo_ammount = float(promo_table_tr_tds[1].text.strip().split('(')[1].split(')')[0][3:])
                promo_ammount = -1 * promo_ammount
                promos_and_tips['split'].append((promo_name, promo_ammount))
                promos_and_tips['total_discount'] -= promo_ammount

            total_bill_table = total_bill_and_promo_tables[1]
            total_bill = float(total_bill_table.tr.findAll('td')[1].text.strip()[3:])

        else:
            total_bill = float(total_bill_and_promo_tables[0].tr.findAll('td')[1].text.strip()[3:])

        check_total = order_total_price + other_costs['total_cost'] + promos_and_tips['tip'] - promos_and_tips['total_discount']
        assert round(check_total, 2) == round(total_bill, 2), f"Bill doesn't add up for order {order_id}"

        order = {}
        order['order_id'] = order_id
        order['restaurant_name'] = res_name
        order['items'] = items
        order['other_costs'] = other_costs
        order['promos_and_tips'] = promos_and_tips
        order['total_cost'] = round(total_bill, 2)
        order['number_of_items'] = len(items)
        order['datetime'] = None
        return order
    except Exception as e:
        print(e, f"for message {message_id}")
        raise Exception


def parse_swiggy(file_path, message_id):
    try:
        with open(file_path, 'r') as fp:
            file_string = fp.read()

        html_string = file_string
        soup = bs4.BeautifulSoup(html_string, "html.parser")

        # Order ID and Restaurant Name
        order_id_and_res_name_div = soup.find('div', {'class': "order-id"})
        order_id_and_res_name_tds = order_id_and_res_name_div.table.tr.findAll('td')

        # Order ID
        order_id_td = order_id_and_res_name_tds[0]
        order_id = order_id_td.h5.text.strip()

        # Restaurant Name
        res_name_td = order_id_and_res_name_tds[1]
        res_name = res_name_td.h5.text.strip()

        # Items, Qty, Costs etc.
        rest_div = soup.find('div', {'class': "order-content"})

        # Item trs
        # ? DS for items:
        # ? ordered_items = [item, item, ...]
        # ? item = {
        # ?   'name','qty','price_per_qty', 'total_price'
        # ? }
        # ? order_total_price = 0
        item_trs = rest_div.table.tbody.findAll('tr', {'style': "margin: 0;padding: 0;"})
        subtotal = 0
        items = []

        # ? Patch to ignore assertion if add-ons were ordered
        add_ons_td = rest_div.table.tbody.findAll('td', {'style': "margin: 0;padding: 5px 0;text-align: left;padding-left:30px;color:#585858;font-weight: normal;border: 0;font-size: 12px;"})
        add_ons_flag = len(add_ons_td) > 0

        for item_tr in item_trs:
            item_tds = item_tr.findAll('td')

            item = {}
            item['name'] = item_tds[0].text.strip()
            item['quantity'] = int(item_tds[1].text.strip())
            item['total_price'] = float(item_tds[2].text.strip())
            item['price_per_unit'] = item['total_price'] / item['quantity']
            subtotal += item['total_price']
            items.append(item)
        # Taxes and Discounts
        # ? Other Costs Data Structure
        # ? other_costs = {
        # ?     'total', 'split' = list of tuples
        # ? tuples = (cost_name, cost)
        # ?}

        # ? Promo discounts and Tip Data Structure
        # ? promos_and_tips = {
        # ? 'total_discount = 0,
        # ? 'split' = list of tuples, each tuple = (promo_name, promo_ammount)
        # ? 'tip' = 0,
        # ? }

        other_costs = {}
        other_costs['total_cost'] = 0
        other_costs['split'] = []

        promos_and_tips = {}
        promos_and_tips['total_discount'] = 0
        promos_and_tips['split'] = []
        promos_and_tips['tip'] = 0

        taxes_and_discounts_table = rest_div.table.tfoot
        t_and_d_trs = taxes_and_discounts_table.findAll('tr')
        for t_and_d_tr in t_and_d_trs:
            th_text = t_and_d_tr.th.text.strip()
            if th_text == 'Cart Subtotal':
                cart_subtotal = float(t_and_d_tr.td.text.strip().split('Rs. ')[1])
                # ? Patch to ignore assertion if add-ons were ordered
                if not add_ons_flag:
                    assert \
                        round(subtotal, 2) == round(cart_subtotal, 2), \
                        f"Total doesn't match for order {order_id}"
            elif th_text == 'Grand Total:':
                total_bill = float(t_and_d_tr.td.text.strip())
            else:
                cost_type = t_and_d_tr.th.text.strip()
                cost_for_given_type = float(t_and_d_tr.td.text.strip().split('Rs. ')[1])
                other_costs['split'].append((cost_type, cost_for_given_type))
                other_costs['total_cost'] += cost_for_given_type

        discount_total = total_bill - (subtotal + other_costs['total_cost'])
        promos_and_tips['total_discount'] = discount_total

        order = {}
        order['order_id'] = order_id
        order['restaurant_name'] = res_name
        order['items'] = items
        order['other_costs'] = other_costs
        order['promos_and_tips'] = promos_and_tips
        order['total_cost'] = round(total_bill, 2)
        order['number_of_items'] = len(items)
        order['datetime'] = None

        return order

    except Exception as e:
        print(e, f"for message {message_id}")
        raise Exception
