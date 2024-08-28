import pandas as pd
from sodapy import Socrata
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_data():
    client = Socrata("data.lacity.org", app_token='jXRSPCTmBeYAiaht4RlaxR23e')
    results = client.get("2nrs-mtv8",limit=10442350)
    return pd.DataFrame.from_records(results)

gender_mapping = {
    "M": "Male",
    "F": "Female"
    }

descent_mapping = {
        "A": "Other Asian",
        "B": "Black",
        "C": "Chinese",
        "D": "Cambodian",
        "F": "Filipino",
        "G": "Guamanian",
        "H": "Hispanic/Latin/Mexican",
        "I": "American Indian/Alaskan Native",
        "J": "Japanese",
        "K": "Korean",
        "L": "Laotian",
        "O": "Other",
        "P": "Pacific Islander",
        "S": "Samoan",
        "U": "Hawaiian",
        "V": "Vietnamese",
        "W": "White",
        "Z": "Asian Indian"
        }

def Categorize(x):
    if (('BATTERY' in x) or ('SIMPLE ASSAULT' in x) or ('OTHER ASSAULT' in x) or ('STALKING' in x) or ('RESISTING ARREST' in x)):
        return 'Other Assault'
    
    elif (('DOCUMENT' in x) or (x in ['COUNTERFEIT'])):
        return 'Forgery AND Counterfieting'
    
    elif (('BUNCO' in x) or ('FRAUD' in x) or (x in ['THEFT OF IDENTITY','GRAND THEFT / AUTO REPAIR','PETTY THEFT - AUTO REPAIR'])):
        return 'Fraud'
    
    elif 'EMBEZZLEMENT' in x:
        return 'Embezzlement'
    
    elif (('VANDALISM' in x) or (x in ['TELEPHONE PROPERTY - DAMAGE','THROWING OBJECT AT MOVING VEHICLE'])):
        return 'Vandalism'
    
    elif x in ['DISCHARGE FIRESARMS/SHOTS FIRED','WEAPONS POSSESSION/BOMBING']:
        return 'Weapon: Carrying,Possesing'
    
    elif x in ['CHILD PORNOGRAPHY','INCEST (SEXUAL ACTS BETWEEN BLOOD RELATIVES)','INDECENT EXPOSURE','LETTERS, LEWD - TELEPHONE CALLS, LEWD','LEWD CONDUCT',
              'LEWD/LASCIVIOUS ACTS WITH CHILD','SEX,UNLAWFUL(INC MUTUAL CONSENT, PENETRATION W/ FRGN OBJ']:
        return 'Sex Offence'
    
    elif x in ['PIMPING','PANDERING']:
        return 'Prostitution And Commercialized Vice'
    
    elif x in ['CHILD ABANDONMENT','CHILD ANNOYING (17YRS & UNDER)',
              'CHILD NEGLECT (SEE 300 W.I.C.)','CHILD STEALING','CRM AGNST CHLD (13 OR UNDER) (14-15 & SUSP 10 YRS OLDER)']:
        return 'Offence Against Family and Children'
    
    elif x in ['BLOCKING DOOR INDUCTION CENTER','DISRUPT SCHOOL','DISTURBING THE PEACE','ILLEGAL DUMPING','PEEPING TOM']:
        return 'Disorderly Conduct'
    
    elif x in ['PROWLER','TRESPASSING','UNAUTHORIZED COMPUTER ACCESS']:
        return 'Vagrancy'
    
    elif x in ['HUMAN TRAFFICKING - COMMERCIAL SEX ACTS', 'HUMAN TRAFFICKING - INVOLUNTARY SERVITUDE','ARSON']:
        return x.capitalize() 
    
    elif x in ['MANSLAUGHTER, NEGLIGENT','CRIMINAL HOMICIDE']:
        return 'Criminal Homicide'
    
    elif x in ['ORAL COPULATION','RAPE, ATTEMPTED','RAPE, FORCIBLE','SEXUAL PENETRATION W/FOREIGN OBJECT','SODOMY/SEXUAL CONTACT B/W PENIS OF ONE PERS TO ANUS OTH']:
        return 'Rape'
    
    elif 'ASSAULT' in x:
        return 'Aggravated Assault'
    
    elif 'BURGLARY' in x:
        return 'Burglary'
    
    elif x in ['ATTEMPTED ROBBERY','ROBBERY']:
        return 'Robbery'
    
    elif 'STOLEN' in x :
        return 'Motor Vehicle Theft'
    
    elif (('THEFT' in x) or ('PICKPOCKET' in x) or ('PURSE SNATCHING' in x) or ('SHOPLIFTING' in x) or ('TILL TAP' in x)):
        return 'Larceny'
    
    else:
        return 'All Other Offence'

def clean_data(data):
    #Drop columns
    data_copy = data.drop(columns=['crm_cd_1','area','weapon_used_cd','status','cross_street','rpt_dist_no','crm_cd','crm_cd_2','crm_cd_3','crm_cd_4'])
    data_copy['date_rptd']= data_copy['date_rptd'].apply(lambda x: x[:10])
    data_copy['date_rptd']= pd.to_datetime(data_copy['date_rptd'])
    data_copy['date_occ']= data_copy['date_occ'].apply(lambda x: x[:10])
    data_copy['date_occ']= pd.to_datetime(data_copy['date_occ'])
    data_copy['day']= data_copy['date_occ'].dt.day_name()
    data_copy['time_occ'] = pd.to_datetime(data_copy['time_occ'], format='%H%M').dt.time
    data_copy['datetime']= pd.to_datetime(data_copy['date_occ'].astype('str') + ' '+ data_copy['time_occ'].astype('str'))
    data_copy['crime_cat'] = data_copy['crm_cd_desc'].apply(Categorize)
    data_copy['lat']= data_copy['lat'].astype(float)
    data_copy['lon']= data_copy['lon'].astype(float)
    data_copy['crime_cat'] = data_copy['crm_cd_desc'].apply(Categorize)
    data_copy['vict_sex'] = data_copy['vict_sex'].map(gender_mapping).fillna("Unknown")
    data_copy['vict_descent'] = data_copy['vict_descent'].map(descent_mapping).fillna("Unknown")
    data_copy.fillna("Unknown",inplace=True)
    data_copy['hover_desc'] = 'Weapon Used: ' + data_copy['weapon_desc'] + '<br>Victim Gender: ' + data_copy['vict_sex'] + '<br>Victim Descent: ' + data_copy['vict_descent'] + '<br>Crime Category: ' + data_copy['crime_cat']
    data_copy = data_copy.drop(columns=['time_occ','date_occ','crm_cd_desc','location','mocodes','status_desc','premis_cd'])

    return data_copy


# def store_data_in_postgres(df,db_params):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        print("Connected")
        cursor = conn.cursor()

        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS crime_reports (
            id SERIAL PRIMARY KEY,
            dr_no VARCHAR(50),
            date_rptd DATE,
            area_name VARCHAR(50),
            part_1_2 VARCHAR(10),
            vict_age VARCHAR(10),
            vict_sex VARCHAR(10),
            vict_descent VARCHAR(50),
            premis_desc VARCHAR(100),
            lat FLOAT,
            lon FLOAT,
            weapon_desc VARCHAR(50),
            day VARCHAR(50),
            datetime TIMESTAMP,
            crime_cat VARCHAR(50),
            hover_desc TEXT
        );
        """
        cursor.execute(create_table_query)
        print("Created The tables")

        # Insert data into the table
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO crime_reports (
                dr_no, date_rptd, area_name, part_1_2, vict_age, vict_sex,
                vict_descent, premis_desc, lat, lon,
                weapon_desc, day,
                datetime, crime_cat, hover_desc
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, tuple(row))
            print(f"Inserting {index}")

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully into PostgreSQL database")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")



def fetch_and_clean_data():
    data = fetch_data()
    print("Fetched")
    transformed_data = clean_data(data)
    print("Transformed")
    return transformed_data
# print("Tranformed")
# db_params = {
#         "host": "localhost",
#         "database": "crime_analytics",
#         "user": "rachitagarwal",
#         "password": os.getenv('LOCALHOST_PASS')
#     }
# store_data_in_postgres(transformed_data,db_params)
# print("Inserted")