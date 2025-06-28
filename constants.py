# Constants
CHANGE_COLS = [
    'ApD_sex_mix_1981_1991_percent_decadal_change',
    'ApD_sex_mix_1991_2001_percent_decadal_change',
    'ApD_sex_mix_2001_2011_percent_decadal_change',
    'QD_1981_1991_percent_decadal_change',
    'QD_1991_2001_percent_decadal_change',
    'QD_2001_2011_percent_decadal_change'
]

CADRE_LABEL_MAPPING = {
    'nurse': 'Nurse',
    'nursing cadres': 'Nurse',
    'dentist': 'Dentist',
    'pharmacist': 'Pharmacist',
    'anm': 'ANM',
    'ayush': 'AYUSH',
    'doctor': 'Doctor',
    'skilled health professionals': 'Skilled Health Professionals',
    'nursing cadres': 'Nursing Cadres',
    'supporting cadres': 'Supporting Cadres'
}

VARNAME_MAPPING = {
    'ApD_cadre_mix_Bhore': 'Acceptability Deficit (ApD) cadre-mix as per Bhore norms',
    'ApD_cadre_mix_HLEG': 'Acceptability Deficit (ApD) cadre-mix as per HLEG norms',
    'ApD_cadre_mix_IHME_UHC80': 'Acceptability Deficit (ApD) cadre-mix as per IHME UHC80 norms',
    'ApD_cadre_mix_IHME_UHC90': 'Acceptability Deficit (ApD) cadre-mix as per IHME UHC90 norms',
    'ApD_cadre_mix_IPHS': 'Acceptability Deficit (ApD) cadre-mix as per IPHS norms',
    'ApD_sex_mix': 'Acceptability Deficit (ApD) sex-mix',

    'AsD': 'Accessibility Deficit (AsD)',

    'AvD_Bhore': 'Availability Deficit (AvD) as per Bhore norms',
    'AvD_HLEG': 'Availability Deficit (AvD) as per HLEG norms',
    'AvD_IHME_UHC80': 'Availability Deficit (AvD) as per IHME UHC80 norms',
    'AvD_IHME_UHC90': 'Availability Deficit (AvD) as per IHME UHC90 norms',
    'AvD_IPHS': 'Availability Deficit (AvD) as per IPHS norms',
    'AvD_MDG': 'Availability Deficit (AvD) as per MDG norms',
    'AvD_SDG': 'Availability Deficit (AvD) as per SDG norms',

    'QD': 'Quality deficit (QD)',

    'AvD_male_Bhore': 'Availability Deficit (AvD) for male population\nas per Bhore norms',
    'AvD_male_HLEG': 'Availability Deficit (AvD) for male population\nas per HLEG norms',
    'AvD_male_HME_UHC80': 'Availability Deficit (AvD) for male population\nas per HME UHC80 norms',
    'AvD_male_IHME_UHC80': 'Availability Deficit (AvD) for male population\nas per IHME UHC80 norms',
    'AvD_male_IHME_UHC90': 'Availability Deficit (AvD) for male population\nas per IHME UHC90 norms',
    'AvD_male_IPHS': 'Availability Deficit (AvD) for male population\nas per IPHS norms',
    'AvD_male_MDG': 'Availability Deficit (AvD) for male population\nas per MDG norms',
    'AvD_male_SDG': 'Availability Deficit (AvD) for male population\nas per SDG norms',
    'AvD_male_UHC_80': 'Availability Deficit (AvD) for male population\nas per UHC80 norms',
    'AvD_male_UHC_90': 'Availability Deficit (AvD) for male population\nas per UHC90 norms',
    'AvD_urban_Bhore': 'Availability Deficit (AvD) for urban population\nas per Bhore norms',
    'AvD_urban_HLEG': 'Availability Deficit (AvD) for urban population\nas per HLEG norms',
    'AvD_urban_HME_UHC80': 'Availability Deficit (AvD) for urban population\nas per HME UHC80 norms',
    'AvD_urban_IHME_UHC80': 'Availability Deficit (AvD) for urban population\nas per IHME UHC80 norms',
    'AvD_urban_IHME_UHC90': 'Availability Deficit (AvD) for urban population\nas per IHME UHC90 norms',
    'AvD_urban_IPHS': 'Availability Deficit (AvD) for urban population\nas per IPHS norms',
    'AvD_urban_MDG': 'Availability Deficit (AvD) for urban population\nas per MDG norms',
    'AvD_urban_SDG': 'Availability Deficit (AvD) for urban population\nas per SDG norms',
    'AvD_urban_UHC_80': 'Availability Deficit (AvD) for urban population\nas per UHC80 norms',
    'AvD_urban_UHC_90': 'Availability Deficit (AvD) for urban population\nas per UHC90 norms',
}

CADRES_OF_INTEREST = (
    'nurse', 'dentist', 'pharmacist', 'anm', 'ayush', 'doctor',
    'skilled health professionals'
)

STATE_ABBR = {
    'andhra pradesh': 'AP',
    'arunachal pradesh': 'AR',
    'assam': 'AS',
    'bihar': 'BR',
    'chhattisgarh': 'CG',
    'goa': 'GA',
    'gujarat': 'GJ',
    'haryana': 'HR',
    'himachal pradesh': 'HP',
    'jammu & kashmir': 'JK',
    'jharkhand': 'JH',
    'karnataka': 'KA',
    'kerala': 'KL',
    'madhya pradesh': 'MP',
    'maharashtra': 'MH',
    'manipur': 'MN',
    'meghalaya': 'ML',
    'mizoram': 'MZ',
    'nagaland': 'NL',
    'odisha': 'OR',
    'punjab': 'PB',
    'rajasthan': 'RJ',
    'sikkim': 'SK',
    'tamil nadu': 'TN',
    'tripura': 'TR',
    'uttarakhand': 'UK',
    'uttar pradesh': 'UP',
    'west bengal': 'WB',
    'andaman & nicobar islands': 'AN',
    'chandigarh': 'CH',
    'dadra & nagar haveli': 'DH',
    'daman and diu': 'DD',
    'n.c.t. of delhi': 'DL',
    'lakshadweep': 'LD',
    'puducherry': 'PY'
}
