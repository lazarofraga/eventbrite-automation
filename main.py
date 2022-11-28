from eventbrite import Eventbrite
import datetime
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
from yaml import safe_load, YAMLError


def get_ticket_classes(eventbrite, event_id):
    classes = eventbrite.get_event_ticket_classes(event_id)
    ticket_ids = {x['id']: x['name'] for x in classes['ticket_classes']}
    # [print(x['category']) for x in classes['ticket_classes']]
    # {print(x, v) for x, v in ticket_ids.items()}
    #eventbrite.get_event_ticket_class_by_id(event_id, ticket_class_id)


def get_ticket_name(eventbrite, event_id, ticket_id):
    classes = eventbrite.get_event_ticket_classes(event_id)
    # print(classes)
    workshop = [x['name']
                for x in classes['ticket_classes'] if x['id'] == str(ticket_id)]
    return workshop[0]


def get_attendee_list(eventbrite, event_id):
    attendees = eventbrite.get(f'/events/{event_id}/attendees/')
    attendee_list = attendees['attendees']
    while attendees['pagination']['has_more_items']:
        continuation_token = attendees['pagination']['continuation']
        attendees = eventbrite.get(
            f'/events/{event_id}/attendees/?continuation={continuation_token}')
        attendee_list.extend(attendees['attendees'])
    return attendee_list


def get_sheet(credentials, sheet_id):
    gclient = gspread.service_account(filename=credentials)
    sheet = gclient.open_by_key(sheet_id)
    return sheet


def update_attendee_sheet(credentials, sheet_id, worksheet_index, dataframe, workshop_title):
    sheet = get_sheet(credentials, sheet_id)
    worksheet = sheet.get_worksheet(worksheet_index)
    worksheet.update([dataframe.columns.values.tolist()] +
                     dataframe.values.tolist())
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    sheet.update_title(f"{workshop_title} Attendee List {timestamp}")

def load_workshops(workshop_yaml):
    with open(workshop_yaml, 'r') as stream:
        try:
            d=safe_load(stream)
        except YAMLError as e:
            print(e)
    return d



def main():

    load_dotenv()
    eventbrite_api_key = os.getenv('EVENTBRITE_API_KEY')
    credentials = os.getenv('CREDENTIALS_PATH')
    workshop_yaml = os.getenv('WORKSHOPS_YAML')
    eventbrite = Eventbrite(eventbrite_api_key)

    workshops = load_workshops(workshop_yaml)
    # print(workshops)

    event_id = workshops['event_id']

    # Get All Attendees
    attendees = get_attendee_list(eventbrite, event_id)
    # Get Workshop Ticket Name

    for workshop in workshops['workshops']:
        workshop_id = workshop['id']
        ticket_name = get_ticket_name(eventbrite, event_id, workshop_id)
        # Filter by Workshop
        attendee_list = [[x['profile']['name'], x['profile']['email']]
                     for x in attendees if x['ticket_class_name'] == ticket_name]
        # Write to Dataframe
        df = pd.DataFrame(attendee_list, columns=['Name', 'Email Address'])
        # Copy to Google Sheet
        sheet_id = workshop['sheet_id']
        update_attendee_sheet(credentials, sheet_id, 0, df, ticket_name)
        # Update Title with Workshop Name and Timestamp


if __name__ == "__main__":
    main()
