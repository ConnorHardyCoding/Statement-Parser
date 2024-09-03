#!/usr/bin/env python3

"""
Runs through files in folder
If file is in correct format
If file already been through skip, else
Reads file and makes list of all the paypal payments in
Creates new dictionary with keys of date, payment ref, amount
Writes to new file in csv format
"""

import re
import os
import csv

# for scanning existing statements
directory = "/Users/connorhardy/Financial-Statements/Bank-statements"
# new folder for output csv files
new_directory = "/Users/connorhardy/Financial-Statements/Bank-statements/HSBC_paypal_statements"
# count for how many new files were created
new_file_count = 0


def file_exists(filename):
    """
    checks that file that gets created doesnt already exist with an output message
    """
    check_file = os.path.join(new_directory, re.sub(r"(.+)_(.+)", r"\1_HSBC_Paypal_\2", filename))    
    output_file_name = re.sub(r"(.+)_(.+)", r"\1_HSBC_Paypal_\2", filename)

    if os.path.exists(check_file):
        print(f"File '{output_file_name}' already exists.")
        return True
    else:
        print(f"File '{output_file_name}' created.")
        return False

def is_correct_file(filename):
    """
    Checks for correct csv statement
    """
    regex_file = r"^(\d{4}-\d{2}-\d{2})_Statement\.csv$"
    # if filename correct and new file doesnt already exist
    if re.search(regex_file, filename) and not file_exists(filename):
        return True
    else:
        return False

def open_file(filename):
    """
    opens file, scans for paypal payments, outputs a list of payments
    """
    regex_date = r"^(\d{2} [A-Za-z]{3} \d{2})"
    regex_paypal = r"^(PAYPAL|PP|EBAY)"
    paypal_list = []
    date = ""
    name = ""
    amount = ""
    paypal = False

    with open(filename) as file:
        for line in file:
            parts = line.strip().replace('"', '').split(",")
            
            # checks for date
            if re.search(regex_date, parts[0]):
                # sets date
                date = parts[0]
                # if payment is paypal
                if re.search(regex_paypal, parts[2]):
                    
                    paypal = True
                    name = parts[2]
                    amount = parts[3]
                    # sometimes payment is in same line
                    if amount:
                        paypal_list.append([date, name, amount])
                        # doesnt need to go to next line to find amount
                        paypal = False

                    continue
            # searches non date lines        
            if re.search(regex_paypal, parts[2]):
                name = parts[2]
                # sets paypal to search next line for amount
                paypal = True
                continue

            # if paypal variable true, set to find amount on next line
            if paypal:
                amount = parts[3]
                paypal_list.append([date, name, amount])
                paypal = False

    return paypal_list   

def convert_list_to_dict_list(paypal_list):
    """
    converts list from open file into a more useful list of dictionaries
    """
    dict_list = []
    for payment in paypal_list:
        # if payment in not payment out
        if payment[2]:
            dict_list.append(dict(date=payment[0], paytype=payment[1], amount=payment[2]))
    return dict_list

def write_file(dict_list, filename):
    global new_file_count
    # new file name
    new_csv_file = re.sub(r"(.+)_(.+)", r"\1_HSBC_Paypal_\2", filename)
    # new file path
    filepath = os.path.join(new_directory, new_csv_file)
    # writes file
    with open(filepath, "w") as file:
        header = dict_list[0].keys()
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(dict_list)

    new_file_count += 1
    
def create_directory(new_directory):
    """
    makes new directory if doesnt already exist
    """
    try:
        os.mkdir(new_directory)
        print(f"New folder created...")
    except FileExistsError:
        print("New folder created previously...")
        pass


def main():
    """
    main program
    """
    create_directory(new_directory)
    for filename in os.listdir(directory):
        if is_correct_file(filename):
            filepath = os.path.join(directory, filename)
            write_file(convert_list_to_dict_list(open_file(filepath)), filename)
    
    print(f"Files created: {new_file_count}")

if __name__ == "__main__":
    main()



