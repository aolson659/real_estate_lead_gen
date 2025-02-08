"""The functions in this script are used to convert web pages to text files. Within these files exist case numbers, which
are used to generate additional URLs to the webpage for a specific court case. The rest of the functions are used to
pull certain data from those webpages. Each of these webpages are structured the same way, allowing this data to be pulled
in a uniform manner. The method for this is a keyword search and additional parsing to filter out excpetions and deliver
clean data to the google sheet."""


import requests
from bs4 import BeautifulSoup
import re
import warnings

warnings.filterwarnings("ignore")

# This function is used to convert the web page to a text file
def get_text(url):
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_text = soup.get_text()
        return all_text
    else:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")
        return None

# Each case number is preceded by the text "CC", this is used to compile a list of case numbers that are then used to generate the URL needed for obtaining case data
def get_case_numbers(url):
    file_content = get_text(url)

    if file_content is not None:
        # Split the text into a list of words for iteration
        words = file_content.split()
    else:
        return None

    case_numbers = []

    for index, word in enumerate(words):
        if word[:2] == 'CC':
            case_numbers.append(word)

    return case_numbers

# Data on defendant name is obtained through a keyword search and further parsing based on web page structure
def get_defendants(url):
    file_content = get_text(url)
    search_word = 'Defendant'

    words = file_content.split()

    defendants = []

    for index, word in enumerate(words):
        if word == search_word:
            # The following logic finds the word 'Defendant' and grabs the following words for further parsing
            if index + 7 <= len(words):
                if 'Sex' not in words [index:index + 7]:
                    defendant = words[index + 3:index + 50]
                    defendants.append((defendant))
    
    # Establish new lists for actual defendant names
    if len(defendants) > 0:
        defendants = defendants[0]
        new_defendants = []
        defendants_final = []

        # Iterate through defendants to remove unnecessary data
        for i in range(len(defendants)):
            if defendants[i].isupper() and '/' not in defendants[i]:
                new_defendants.append(defendants[i])
            else:
                joined_string = " ".join(new_defendants)  
                new_defendants = []
                defendants_final.append(joined_string)
        defendants_final = [item for item in defendants_final if item != '']

        # Further parsing was needed to remove certain words that were identified earlier
        if len(defendants_final) > 0:
            if len(defendants_final[-1]) == 3:
                joined_string = " ".join(defendants[0:3])
                defendants_final = []
                defendants_final.append(joined_string)
        else:
            defendants_final = []
            defendants_final = defendants[0:3]
            for i in range(len(defendants_final)):
                if defendants_final[i] == 'Relationship':
                    del defendants_final[i]
            joined_string = " ".join(defendants_final)
            defendants_final = []
            defendants_final.append(joined_string)


        return defendants_final
    else:
        return None


# This function pulls the plaintiff for each case
def get_plaintiff(url):
    file_content = get_text(url)

    words = file_content.split()
    plaintiff = []
    search_word = 'Plaintiff'
    # Iterates through the text file for the search word then parses the data based on the structure of the web page
    for index, word in enumerate(words):
        if word == search_word:
            if index + 7 <= len(words) and 'Sex' not in words[index:index + 7]:
                end_index = words.index('Relationship', index)
            
                plaintiff = words[index + 3:end_index]

                plaintiff = ' '.join(plaintiff)
                break
    return plaintiff

# This function finds whether or not the judgment was satisfied by searching the text file for a specific pattern
def get_judgments(url):
    file_content = get_text(url)

    words = file_content.split()
    plaintiff = []
    search_word = 'Judgments'
    for index, word in enumerate(words):
        
        if word == search_word:
            if words[index + 1:index + 2] == ['There'] and words[index + 2:index + 3] == ['are'] and words[index + 3:index + 4] == ['no'] and words[index + 4:index + 5] == ['judgments']:
                judgments = 'N'
                judgment_date = 'N/A'
                return judgments, judgment_date
            else:
                judgments = 'Y'
                pattern = r"Judgments.*?(\d{1,2}/\d{1,2}/\d{4})"

                match = re.search(pattern, file_content, re.DOTALL)
                judgment_date = match.group(1)

                return judgments, judgment_date
            
# This function finds the charges the defendants owe to the plaintiff, what each charge is, how much each charge is, and what the total amount owed is
def get_amounts(url):
    file_content = get_text(url)
    words = file_content.split()
    search_word = '$'
    rent = []
    attorney_fees = []
    tax = []
    late_charge = []
    notice_fees = []
    costs = []
    undesignated = []
    utilities = []
    total_judgment = []
    for index, word in enumerate(words):
        
        if search_word in word:
            if words[index + 1:index + 2] == ['Total']:
                if ',' in word:
                    total_judgment.append(float(word.replace('$', '').replace(',', '')))
                    break
                else:
                    total_judgment.append(float(word.replace('$', '')))
                    break
            if words[index + 1:index + 2] == ['Attorney']:
                if ',' in word:
                    attorney_fees.append(float(word.replace('$', '').replace(',', '')))
                else:
                    attorney_fees.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Costs']:
                if ',' in word:
                    costs.append(float(word.replace('$', '').replace(',', '')))
                else:
                    costs.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Utilities']:
                if ',' in word:
                    utilities.append(float(word.replace('$', '').replace(',', '')))
                else:
                    utilities.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Undesignated']:
                if ',' in word:
                    undesignated.append(float(word.replace('$', '').replace(',', '')))
                else:
                    undesignated.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Tax']:
                if ',' in word:
                    tax.append(float(word.replace('$', '').replace(',', '')))
                else:
                    tax.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Notice']:
                if ',' in word:
                    notice_fees.append(float(word.replace('$', '').replace(',', '')))
                else:
                    notice_fees.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Late']:
                if ',' in word:
                    late_charge.append(float(word.replace('$', '').replace(',', '')))
                else:
                    late_charge.append(float(word.replace('$', '')))
            if words[index + 1:index + 2] == ['Rent']:
                if ',' in word:
                    rent.append(float(word.replace('$', '').replace(',', '')))
                elif '(' in word and ')' in word:
                    late_charge.append(float(word.replace('$', '').replace('(', '').replace(')', '')))
                else:
                    late_charge.append(float(word.replace('$', '')))

    if len(total_judgment) == 0:
        total_judgment = 0
    else:
        total_judgment = sum(total_judgment)
    if len(attorney_fees) == 0:
        attorney_fees = 0
    else:
        attorney_fees = sum(attorney_fees)
    if len(costs) == 0:
        costs = 0
    else:
        costs = sum(costs)
    if len(utilities) == 0:
        utilities = 0
    else:
        utilities = sum(utilities)
    if len(undesignated) == 0:
        undesignated = 0
    else:
        undesignated = sum(undesignated)
    if len(tax) == 0:
        tax = 0
    else:
        tax = sum(tax)
    if len(notice_fees) == 0:
        notice_fees = 0
    else:
        notice_fees = sum(notice_fees)
    if len(late_charge) == 0:
        late_charge = 0
    else:
        late_charge = sum(late_charge)
    if len(rent) == 0:
        rent = 0
    else:
        rent = sum(rent)

    

    total_amount = (total_judgment) + (attorney_fees) + (costs) + (utilities) + (undesignated) + (tax) + (notice_fees) + (late_charge) + (rent)

    return total_amount, rent, attorney_fees, tax, utilities, late_charge, notice_fees, costs, undesignated

if __name__ == '__main__':
    # This will run a test to see if the data is being pulled correctly based off a provided URL


    url = 'https://justicecourts.maricopa.gov/app/courtrecords/CaseInfo?casenumber=CC2023017083000'
    text = get_text(url)
    case_number = get_case_numbers(url)  
    defendants = get_defendants(url)
    plaintiff = get_plaintiff(url) 
    judgments, judgment_date = get_judgments(url)
    total_amount, rent, attorney_fees, tax, utilities, late_charge, notice_fees, costs, undesignated = get_amounts(url) 
    print('Case Number:', case_number)
    print('Defendants', defendants)  
    print('Plaintiff:', plaintiff)
    print('Judgment', judgments)
    print('Judgment Date', judgment_date)
    print('Rent', rent)
    print('Attorney Fees', attorney_fees)
    print('Tax', tax)
    print('Utilities', utilities)
    print('Late Charges', late_charge)
    print('Notice Fees', notice_fees)
    print('Costs', costs)
    print('Undesignated', undesignated)
    print('Total Amount', total_amount)



