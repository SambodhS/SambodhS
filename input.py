import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd
import time

# --------- Prompt for download option ------------
download_choice = input("Would you like to download the latest tags or use an existing file? (D/E): ").strip().lower()

if download_choice.startswith("d"):
    from selenium import webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    EMAIL = "sambodh.sinha@vanderbilt.edu"
    PASSWORD = "Sambodhmimansa"
    driver = webdriver.Chrome()

    try:
        driver.get("https://app.spiideo.net/sign-in")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        ).send_keys(EMAIL)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        ).send_keys(PASSWORD)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.url_changes("https://app.spiideo.net/sign-in")
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'I accept')]"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'games-list-item-module__wrapper__')]"))
        ).click()
        info_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'segmented-control-module__control__') and contains(., 'Info')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", info_tab)
        info_tab.click()
        export_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Export tags']/ancestor::a[@href]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", export_link)
        ActionChains(driver).move_to_element(export_link).click().perform()
        print("Export initiated. Waiting for download...")
    except Exception as e:
        print(f"Error during automation: {e}")
    finally:
        time.sleep(1)
        driver.quit()
else:
    print("Using existing file.")

ALL_PLAYERS = [
    "Adysen", "Alexa", "Ally", "Ava", "Courtney", "Ellett", "Emelia",
    "Hannah", "Kennadie", "Maci", "Margo", "MB", "Melania", "Neliaj",
    "Nyela", "Sydney", "Vivian", "Wojo", "Other"
]

GOALKEEPERS = ["Alexa", "Kennadie", "Wojo", "Neliaj"]

# ------------------- Parse XML File -------------------
def parse_xml_to_dataframe(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    data = []
    for instance in root.findall('.//instance'):
        code_elem = instance.find('code')
        code = code_elem.text.strip() if code_elem is not None else ''
        label_elem = instance.find('label/text')
        label = label_elem.text.strip() if label_elem is not None else ''
        time_elem = instance.find('start')
        time_val = time_elem.text.strip() if time_elem is not None else ''
        data.append({
            'Event Code': code,
            'Label Text': label,
            'Time': time_val
        })
    return pd.DataFrame(data)


# ------------------- Calculate Stats -------------------
def calculate_stats(df):
    player_stats = pd.DataFrame({
        'Player': ALL_PLAYERS,
        'Shots': 0,
        'Shots on Goal': 0,
        'Goals': 0,
        'Goal tackle': 0,
        'Cross +': 0,
        'Cross -': 0,
        'Build +': 0,
        'Build -': 0,
        'Turnover': 0,
        'Assist': 0,
        'Box entry +': 0,
        'Box entry -': 0
    }).set_index('Player')

    gk_stats = pd.DataFrame({
        'Goalkeeper': GOALKEEPERS,
        'Shots Faced': 0,
        'Saves': 0,
        'Goals Conceded': 0
    }).set_index('Goalkeeper')

    training_vars = ['Cross +', 'Cross -', 'Build +', 'Build -', 'Assist', 'Turnover', 'Goal tackle', 'Box entry +', 'Box entry -']

    game_vars = [
        "Shot ON", "Shot OFF", "Inside box shot", "Box entry +", "Box entry -", "Build +", "Build -", "Att Half Recoveries",
        "(O) Box entry +", "(O) Box entry -", "(O) Shot ON", "(O) Shot OFF", "(O) Inside box shot",
        "Att Corner +", "Att Corner -", "Att Free Kick +", "Att Free Kick -", "F3rd Th In +", "F3rd Th In -", "Mid Th In +",
        "Mid Th In -", "D3rd Th In +", "D3rd Th In -", "Def Corner +", "Def Corner -", "Def Free Kick +", "Def Free Kick -",
        "F3rd ThAg +", "F3rd ThAg -", "Mid ThAg +", "Mid ThAg -", "D3rd ThAg +", "D3rd ThAg -"
    ]

    for _, row in df.iterrows():
        event = row['Event Code']
        label = row['Label Text']
        # t = float(row['Time'])

        if event in training_vars:
            if label in ALL_PLAYERS:
                col = event
                player_stats.loc[label, col] += 1
            continue

        # Shot OFF
        if event in ALL_PLAYERS and label == '':
            player_stats.loc[event, 'Shots'] += 1

        # Shot ON/Save
        elif event in GOALKEEPERS and label in ALL_PLAYERS:
            player_stats.loc[label, 'Shots on Goal'] += 1
            player_stats.loc[label, 'Shots'] += 1
            gk_stats.loc[event, 'Saves'] += 1
            gk_stats.loc[event, 'Shots Faced'] += 1

        # Goal
        elif event in ALL_PLAYERS and label in GOALKEEPERS:
            player_stats.loc[event, 'Goals'] += 1
            player_stats.loc[event, 'Shots'] += 1
            player_stats.loc[event, 'Shots on Goal'] += 1
            gk_stats.loc[label, 'Goals Conceded'] += 1
            gk_stats.loc[label, 'Shots Faced'] += 1

        # GAME STATS
        if event in game_vars:
            game_stats[event] += 1

    game_stats_df = pd.DataFrame([game_stats])

    return (
        player_stats.reset_index(),
        gk_stats.reset_index(),
        game_stats_df
    )


stats_choice = input("Do you want training stats (T) or game stats (G)?: ").strip().lower()

DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
xml_files = glob.glob(os.path.join(DOWNLOADS_DIR, "*.xml"))
if not xml_files:
    print("No XML file found in Downloads directory!")
    exit()

latest_xml = xml_files[0]
df = parse_xml_to_dataframe(latest_xml)

player_table, gk_table, general_table = calculate_stats(df)

if stats_choice.startswith("t"):
    player_table.to_csv("infield_stats.csv", index=False)
    gk_table.to_csv("goalkeeper_stats.csv", index=False)
elif stats_choice.startswith("g"):
    general_table.to_csv("game_stats.csv", index=False)
    row = general_table.iloc[0]
    creation_df = pd.DataFrame({
        "category": ["complete", "incomplete"],
        "count": [row["Box entry +"], row["Box entry -"]]
    })
    creation_df.to_csv("creation.csv", index=False)

    progression_df = pd.DataFrame({
        "category": ["Final 3rd Progression", "Att Half Recoveries"],
        "count": [row["Final 3rd Progression"], row["Att Half Recoveries"]]
    })
    progression_df.to_csv("progression.csv", index=False)

    finishing_df = pd.DataFrame({
        "category": ["shots_on", "shots_off"],
        "count": [row["Shot ON"], row["Shot OFF"]]
    })
    finishing_df.to_csv("finishing.csv", index=False)

    build_df = pd.DataFrame({
        "category": ["successful", "unsuccessful"],
        "count": [row["Build +"], row["Build -"]]
    })
    build_df.to_csv("build.csv", index=False)
