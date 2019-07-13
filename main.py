import json

from quickstart import generate_service
from gmail_funcs import get_all_messages, get_label_ids
from gmail_funcs import generate_label_json_data


service = generate_service()
label_names = ['Zomato Only', 'Swiggy Only']
user_id = 'me'
labels = get_label_ids(service, label_names)
message_ids_all_labels = get_all_messages(service, labels, user_id=user_id)

label = message_ids_all_labels[0]  # ? Zomato
# label = message_ids_all_labels[1]  # ? Swiggy
start = 0  # ! 0 to parse from the latest message
end = -1  # ! -1 to parse till the oldest message
final_data = generate_label_json_data(service, user_id, label, start=start, end=end)

if label['name'] == 'Swiggy Only':
    path = 'swiggy_data.json'
    with open(path, 'w', encoding='UTF-8') as fp:
        fp.write(json.dumps(final_data, indent=4))

if label['name'] == 'Zomato Only':
    path = 'zomato_data.json'
    with open(path, 'w', encoding='UTF-8') as fp:
        fp.write(json.dumps(final_data, indent=4))
