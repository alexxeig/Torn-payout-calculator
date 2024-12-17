import csv
import pandas as pd

#Leaves only needed faction/members in the RW report csv.
def extract_faction_members(input_file, faction_name, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    start_processing = False
    members = []
    header = ""

    for line in lines:
        stripped_line = line.strip()
        if stripped_line == f'"{faction_name}"':
            start_processing = True
            members = []
            continue

        if start_processing:
            if stripped_line == '"Members";"Level";"Attacks";"Score"':
                header = stripped_line
                continue
            elif stripped_line.startswith('"') and stripped_line.endswith(
                    '"') and '[' in stripped_line and ']' in stripped_line:
                members.append(stripped_line)
            else:
                start_processing = False

    with open(output_file, 'w') as file:
        if header:
            file.write(f'{header}\n')
        for member in members:
            file.write(f'{member}\n')

#Processs RW report csv and makes a dictionary.
def rw_report_import(csv_file):
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        data_dict = {}
        for row in reader:
            member = row['Members']
            data_dict[member] = {
                'RW Hits': row['Attacks'],
                'RW Score': row['Score']
            }
    return data_dict

#Processes attacks report csv and creates a dictionary of all attacks made.
def attacks_report_import(csv_file):
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        data_dict = {}
        for row in reader:
            attack = row['tId']
            data_dict[attack] = {
                'Attacker Faction ID': row[' attacker_faction'],
                'Attacker Faction': row[' attacker_factionname'],
                'Attacker': row[' attacker_name'],
                'Attacker ID': row[' attacker_id'],
                'Defender Faction': row[' defender_factionname'],
                'Defender Faction ID': row[' defender_faction'],
                'Defender': row[' defender_name'],
                'Defender ID': row[' defender_id'],
                'Result': row[' result'],
                'Respect Gained': row[' respect_gain'],
                'Chain hit Nr': row[' chain'],
                'Fair Fight Multiplier': row[' fair_fight'],
                'War Attack': row[' war'],
                'Retal Attack': row[' retaliation'],
                'Group Attack': row[' group_attack'],
                'Overseas Attack': row[' overseas'],
                'Chain multiplier': row[' chain_bonus'],
                'Warlord bonus': row[' warlord_bonus'],
                'Code': row[' code']
            }
    return data_dict

#Fixes leading empty characters.
def strip_dict_values(dictionary):
    """
    Recursively strips leading and trailing spaces from all string values in a dictionary.

    Args:
    d (dict): The dictionary to process.

    Returns:
    dict: The processed dictionary with stripped string values.
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recursively process it
            dictionary[key] = strip_dict_values(value)
        elif isinstance(value, str):
            # If the value is a string, strip leading and trailing spaces
            dictionary[key] = value.strip()
    return dictionary

#Removes decimal separators
def fix_rwreport_score():
    for member, member_details in rw_dict.items():
        member_details['RW Score'] = float(member_details['RW Score'].replace(',', ''))
        member_details['RW Hits'] = int(member_details['RW Hits'])

rw_report = 'report.csv'
attacks_report = 'attacks.csv'
our_faction = ' '
opponent_faction = ' '
assist_multiplier = 4
chain_multiplier = 1
payout_pot = 2814210660

extract_faction_members(rw_report, our_faction, rw_report)
rw_dict = rw_report_import(rw_report)
attacks_dict = attacks_report_import(attacks_report)
stripped_attacks = strip_dict_values(attacks_dict)
fix_rwreport_score()

def calculateAvgRespect():
    for member, details in rw_dict.items():
        if details['RW Score'] != 0:
            details['Avg respect per hit'] = round((details['RW Score'] / details['RW Hits']), 2)
        else:
            details['Avg respect per hit'] = 0
def calculateMemberAssists():
    for member, member_details in rw_dict.items():
        assist_counter = 0
        for attack, attack_details in stripped_attacks.items():
            name = f'{attack_details['Attacker']} [{attack_details['Attacker ID']}]'
            conditions = ('Assist', 'Lost')
            if (name == member and
                attack_details['Defender Faction'] == opponent_faction and
                attack_details['Result'] in conditions
            ):
                assist_counter += 1
        member_details['Assists'] = assist_counter
def calculateMemberChainHits():
    for member, member_details in rw_dict.items():
        chain_hit_counter = 0
        for attack, attack_details in stripped_attacks.items():
            name = f'{attack_details['Attacker']} [{attack_details['Attacker ID']}]'
            conditions = ('Attacked', 'Mugged', 'Hospitalized')
            if (name == member and
                attack_details['Result'] in conditions and
                attack_details['Defender Faction'] != opponent_faction
            ):
                chain_hit_counter += 1
        member_details['Outside Hits'] = chain_hit_counter
def adjustForBonusHits():
    for member, member_details in rw_dict.items():
        for attack, attack_details in stripped_attacks.items():
            chain_bonus_hits = (10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000)
            name = f'{attack_details['Attacker']} [{attack_details['Attacker ID']}]'
            if (name == member and
                int(attack_details['Chain hit Nr']) in chain_bonus_hits
            ):
                member_details['RW Score'] -= float(attack_details['Respect Gained'])
                member_details['RW Score'] = round(member_details['RW Score'], 2)
def calculateTotalMemberPoints():
    total_points_scored = 0
    for member, member_details in rw_dict.items():
        personal_points = (member_details['Assists'] * assist_multiplier) + (member_details['Outside Hits'] * chain_multiplier) + member_details['RW Score']
        member_details['Total Points'] = round(personal_points, 2)
        total_points_scored += personal_points
    return total_points_scored
def calculatePayout():
    for member, member_details in rw_dict.items():
        member_details['Money Earned'] = int(member_details['Total Points'] * (payout_pot / total_points))

calculateAvgRespect()
calculateMemberAssists()
calculateMemberChainHits()
adjustForBonusHits()
total_points = round(calculateTotalMemberPoints(), 2)
calculatePayout()

def showEverything():
    pot_test = 0
    for i, j in rw_dict.items():
        print(i, j)
        pot_test = pot_test + j['Money Earned']
    print(total_points)
    print(pot_test)
def exportToExcel():
    data_transformed = []
    for member, member_detail in rw_dict.items():
        new_entry = {'Name': member}
        new_entry.update(member_detail)
        data_transformed.append(new_entry)
    df = pd.DataFrame(data_transformed)
    excel_file_path = 'payouts.xlsx'
    df.to_excel(excel_file_path, index=False)
def generate_link(record_name, record_data):
    user_id = record_name.split('[')[-1].strip(']')
    money_earned = record_data['Money Earned']
    link = f"https://www.torn.com/factions.php?step=your#/tab=controls&option=give-to-user&addMoneyTo={user_id}&money={money_earned}"
    return link
def runLinkGeneration():
    with open('links.txt', 'w') as file:
        for record_name, record_data in rw_dict.items():
            link = generate_link(record_name, record_data)
            file.write(link + '\n')

showEverything()
# exportToExcel()
# runLinkGeneration()



