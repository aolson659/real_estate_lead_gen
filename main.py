'''This is the main script to be ran, it works by generating URLs based off mobile home park names and case numbers. The URLs
are generated and verification is done to determine if desirable data is present within the web page. It then calls the
functions in parse_data to pull the data, compile them into a dataframe, and send them to a google sheet for the client.'''

from bs4 import BeautifulSoup
import gspread
from gspread_dataframe import set_with_dataframe
import time
import traceback
import pandas as pd
import warnings

import parse_data

warnings.filterwarnings("ignore")

# This function is used when sending data to the google sheet, making sure it is sent to the next empty row
def find_next_empty_row(sheet):
    col_values = sheet.col_values(1)
    
    next_empty_row = col_values.index('') + 1 if '' in col_values else len(col_values) + 1
    
    return next_empty_row
    


def get_url(year, sheet_id, sheet_name):

    # Configuration file for google cloud api is required for this script to work
    cred_file = "your_google_cloud_json_file"
    gc = gspread.service_account(cred_file)

    # Google file with park list data and sheets for data to be sent to
    park_data = gc.open("EVICTION records - Chaparral A MHP")

    # List of mobile home parks
    park_list_sheet = park_data.worksheet(sheet_id)

    column_1_values = park_list_sheet.col_values(1)[1:]

    # URL template used to generate new URLs for each court case search
    base_url = "https://justicecourts.maricopa.gov/app/courtrecords/caseSearchResults?bName="

    # Generate dataframe used to send data
    df = pd.DataFrame(columns=['plaintiff', 'hyperlink_formula', 'defendants', 'judgments', 'judgment_date', 'total_amount', 'rent', 'attorney_fees', 'tax', 'utilities', 'late_charge', 'notice_fees', 'costs', 'undesignated'])


    for value in column_1_values:
        try:
            # Check to see length of data, data is sent in batches of 20 to limit api calls
            if len(df) >= 20:
                    sheet = park_data.worksheet(sheet_name)
                    next_empty_row = find_next_empty_row(sheet)
                    set_with_dataframe(sheet, df, row=next_empty_row, include_index=False, include_column_header=False)
                    df.drop(df.index, inplace=True)
                    print()
                    print('Data Sent')
                    print()



            # Delays are present throughout the script to prevent api limits from being reached
            time.sleep(12)

            # Split name of mobile home park pulled from list into seperate words
            words = value.split()
            
            # Reset url to base url for each new search
            url = base_url

            # Iterate through mobile home park name and add them to search URL
            for i in range(len(words)):
                name_in_url = words[i] + '%20'
                url += name_in_url

            url = url.rstrip('%20')
            url = url + f'&year={year}'


            print('URL:', url)
            # Generate list of case numbers from search URL, each mobile home park is typically involved in multiple cases
            case_numbers = parse_data.get_case_numbers(url)
            if case_numbers is not None:
                # If no case numbers are returned, retry search with certain keywords removed, removing these words allows for a broader search
                if len(case_numbers) == 0:
                    words = [element.lower() for element in words]
                    new_words = [word for word in words if word not in ['mobile', 'rv', 'park', 'home', 'subdivision', 'resort', 'estate', 'estates', 'community', 'trailer']]


                    url = base_url
                    for i in range(len(new_words)):
                        name_in_url = new_words[i] + '%20'
                        url += name_in_url

                    url = url.rstrip('%20')
                    url = url + f'&year={year}'
                    case_numbers = parse_data.get_case_numbers(url)

                # If case numbers are returned, these are used to generate new URLs for each case, where the data sent to the google sheet is pulled from
                if len(case_numbers) > 0:
                    time.sleep(12)
                    for i in range(len(case_numbers)):
                        try:
                            # Generate new URL using case numbers
                            print('Case Number:', case_numbers[i])
                            url = f"https://justicecourts.maricopa.gov/app/courtrecords/CaseInfo?casenumber={case_numbers[i]}" + "000"
                            link_text = f"{case_numbers[i]}"
                            hyperlink_formula = f'=HYPERLINK("{url}", "{link_text}")'
                            print(url)
                            # Pull desired data from generated URLs
                            plaintiff = parse_data.get_plaintiff(url)
                            defendants = parse_data.get_defendants(url)
                            if defendants is not None:
                                judgments, judgment_date = parse_data.get_judgments(url)
                                total_amount, rent, attorney_fees, tax, utilities, late_charge, notice_fees, costs, undesignated = parse_data.get_amounts(url)
                                if len(defendants) > 0:
                                    if len(defendants) > 1:
                                        names_list = defendants
                                        defendants = ', '.join(names_list)
                                        if isinstance(defendants, list) and all(isinstance(item, (int, float, str)) for item in defendants):
                                            pass
                                        else:
                                            defendants = [defendants]
                                        data_to_send = [plaintiff, hyperlink_formula, defendants, judgments, judgment_date, total_amount, rent, attorney_fees, tax, utilities, late_charge, notice_fees, costs, undesignated]
                                        # Generate datafram with data to be sent to google sheet
                                        new_data = pd.DataFrame({
                                            'plaintiff': [plaintiff],
                                            'hyperlink_formula': hyperlink_formula,
                                            'defendants': [defendants[-1]],
                                            'judgments': [judgments],
                                            'judgment_date': [judgment_date],
                                            'total_amount': [total_amount],
                                            'rent': [rent],
                                            'attorney_fees': [attorney_fees],
                                            'tax': [tax],
                                            'utilities': [utilities],
                                            'late_charge': [late_charge],
                                            'notice_fees': [notice_fees],
                                            'costs': [costs],
                                            'undesignated': [undesignated]
                                        })

                                        df = pd.concat([df, new_data], ignore_index=True)

                                        print('Plaintiff:', plaintiff)
                                        print('Defendants:', defendants)
                                    else:
                                        
                                        new_data = pd.DataFrame({
                                            'plaintiff': [plaintiff],
                                            'hyperlink_formula': hyperlink_formula,
                                            'defendants': [defendants[-1]],
                                            'judgments': [judgments],
                                            'judgment_date': [judgment_date],
                                            'total_amount': [total_amount],
                                            'rent': [rent],
                                            'attorney_fees': [attorney_fees],
                                            'tax': [tax],
                                            'utilities': [utilities],
                                            'late_charge': [late_charge],
                                            'notice_fees': [notice_fees],
                                            'costs': [costs],
                                            'undesignated': [undesignated]
                                        })

                                        df = pd.concat([df, new_data], ignore_index=True)

                                        print('Plaintiff:', plaintiff)
                                        print('Defendants:', defendants[-1])
                                
                        except Exception as e:
                            tb = traceback.format_exc()
                            print(f"An error occurred: {e}\nTraceback: {tb}")
                            time.sleep(60)
                            continue
                
        except Exception as e:
            tb = traceback.format_exc()
            print(f"An error occurred: {e}\nTraceback: {tb}")
            time.sleep(60)
            continue



if __name__ == '__main__':
    sheet_id = 'EVICTION records - Chaparral A MHP'
    sheet_name = 'test_sheet'
    get_url(2025, sheet_id, sheet_name)