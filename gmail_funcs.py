import base64
import email
import os

from parsers import parse_new_zomato, parse_swiggy


def get_label_ids(service, label_names):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    label_ids = []
    if not labels:
        print('No labels found.')
    else:
        for label in labels:
            if label['name'] in label_names:
                label_ids.append((label['id'], label['name']))
    return label_ids


def list_messages_with_labels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

    Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
    """

    response = service.users().messages().list(
        userId=user_id,
        labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def get_all_messages(service, labels, user_id='me'):
    final_messages_list = []
    for label in labels:
        label_data = service.users().labels().get(
            userId=user_id,
            id=label[0]).execute()
        if label_data['messagesTotal'] != label_data['threadsTotal']:
            raise InterruptedError(
                f"Number of threads({label_data['threadsTotal']}) != "
                f"Number of messages({label_data['messagesTotal']})"
                f"for label {label[1]}"
            )
        messages_list = list_messages_with_labels(
            service,
            user_id,
            label_ids=label[0]
        )
        final_messages_list.append(
            {
                'name': label[1],
                'data': messages_list
            }
        )
    return final_messages_list


def generate_label_json_data(service, user_id, label, start=0, end=-1):

    final_data = {}
    label_name = label['name']
    if label_name == 'Zomato Only':
        final_data['Zomato'] = []
    if label_name == 'Swiggy Only':
        final_data['Swiggy'] = []

    iter_ = start
    for message in label['data'][start:end]:
        message_id = message['id']

        api_message = service.users().messages().get(
            userId=user_id,
            id=message_id,
            format='full').execute()
        msg_str = base64.urlsafe_b64decode(
            api_message['payload']['body']['data'].encode('UTF8'))
        msg_str = msg_str.decode('UTF-8')
        mime_msg = email.message_from_string(msg_str)
        html_string = mime_msg.get_payload()

        # Datetime from email
        # Format is 'Wed, 19 Jun 2019 07:00:17'
        # msg_datetime = datetime.strptime(datetime_sting, '%a, %d %b %Y %H:%M:%S')
        for header in api_message['payload']['headers']:
            if header['name'] == 'Date':
                datetime_sting = header['value'].split('+')[0].strip()
                break

        path = os.path.join('temp', 'test.html')
        with open(path, 'w', encoding='UTF-8') as fp:
            fp.write(html_string)

        if label_name == 'Swiggy Only':
            iter_ += 1
            print(f"Iteration {iter_} -- Parsing message_id = {message_id}")

            order = parse_swiggy(path, message_id)
            order['datetime'] = datetime_sting
            final_data['Swiggy'].append((message_id, order))

        if label_name == 'Zomato Only':
            for header in api_message['payload']['headers']:
                if header['name'] == 'Subject' and header['value'][:22] == 'Your Zomato order from':
                    print(f"Iteration {iter_} -- Parsing message_id = {message_id}")
                    iter_ += 1
                    order = parse_new_zomato(path, message_id)
                    order['datetime'] = datetime_sting
                    final_data['Zomato'].append((message_id, order))

                if header['name'] == 'Subject' and header['value'][:27] == 'Summary for your order with':
                    print(f"Iteration {iter_} -- Parsing (OLD) message_id = {message_id}")
                    iter_ += 1
                    order = parse_new_zomato(path, message_id)
                    order['datetime'] = datetime_sting
                    final_data['Zomato'].append((message_id, order))

    return final_data
