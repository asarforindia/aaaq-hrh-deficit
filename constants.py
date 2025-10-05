# Constants

# Columns to drop from the raw data
CHANGE_COLS = [
    "ApD_sex_mix_1981_1991_percent_decadal_change",
    "ApD_sex_mix_1991_2001_percent_decadal_change",
    "ApD_sex_mix_2001_2011_percent_decadal_change",
    "QD_1981_1991_percent_decadal_change",
    "QD_1991_2001_percent_decadal_change",
    "QD_2001_2011_percent_decadal_change",
]

# Mapping of cadre names to labels
CADRE_LABEL_MAPPING = {
    "nurse": "Nurse",
    "nursing cadres": "Nurse",
    "dentist": "Dentist",
    "pharmacist": "Pharmacist",
    "anm": "ANM",
    "ayush": "AYUSH",
    "doctor": "Doctor",
    "skilled health professionals": "Skilled Health Professionals",
    "nursing cadres": "Nursing Cadres",
    "supporting cadres": "Supporting Cadres",
}

# Mapping of variable names to labels
VARNAME_MAPPING = {
    # Acceptability Deficit (ApD)
    "ApD_cadre_mix_Bhore": "Acceptability Deficit (ApD) cadre-mix as per Bhore norms",
    "ApD_cadre_mix_HLEG": "Acceptability Deficit (ApD) cadre-mix as per HLEG norms",
    "ApD_cadre_mix_IHME_UHC80": "Acceptability Deficit (ApD) cadre-mix as per IHME UHC80 norms",
    "ApD_cadre_mix_IHME_UHC90": "Acceptability Deficit (ApD) cadre-mix as per IHME UHC90 norms",
    "ApD_cadre_mix_IPHS": "Acceptability Deficit (ApD) cadre-mix as per IPHS norms",
    "ApD_sex_mix": "Acceptability Deficit (ApD) sex-mix",
    # Accessibility Deficit (AsD)
    "AsD": "Accessibility Deficit (AsD)",
    # Quality Deficit (QD)
    "QD": "Quality deficit (QD)",
    # Availability Deficit (AvD)
    "AvD_Bhore": "Availability Deficit (AvD) as per Bhore norms",
    "AvD_HLEG": "Availability Deficit (AvD) as per HLEG norms",
    "AvD_IHME_UHC80": "Availability Deficit (AvD) as per IHME UHC80 norms",
    "AvD_IHME_UHC90": "Availability Deficit (AvD) as per IHME UHC90 norms",
    "AvD_IPHS": "Availability Deficit (AvD) as per IPHS norms",
    "AvD_MDG": "Availability Deficit (AvD) as per MDG norms",
    "AvD_SDG": "Availability Deficit (AvD) as per SDG norms",
    "AvD_male_Bhore": "Availability Deficit (AvD) for male population\nas per Bhore norms",
    "AvD_male_HLEG": "Availability Deficit (AvD) for male population\nas per HLEG norms",
    "AvD_male_HME_UHC80": "Availability Deficit (AvD) for male population\nas per HME UHC80 norms",
    "AvD_male_IHME_UHC80": "Availability Deficit (AvD) for male population\nas per IHME UHC80 norms",
    "AvD_male_IHME_UHC90": "Availability Deficit (AvD) for male population\nas per IHME UHC90 norms",
    "AvD_male_IPHS": "Availability Deficit (AvD) for male population\nas per IPHS norms",
    "AvD_male_MDG": "Availability Deficit (AvD) for male population\nas per MDG norms",
    "AvD_male_SDG": "Availability Deficit (AvD) for male population\nas per SDG norms",
    "AvD_male_UHC_80": "Availability Deficit (AvD) for male population\nas per UHC80 norms",
    "AvD_male_UHC_90": "Availability Deficit (AvD) for male population\nas per UHC90 norms",
    "AvD_urban_Bhore": "Availability Deficit (AvD) for urban population\nas per Bhore norms",
    "AvD_urban_HLEG": "Availability Deficit (AvD) for urban population\nas per HLEG norms",
    "AvD_urban_HME_UHC80": "Availability Deficit (AvD) for urban population\nas per HME UHC80 norms",
    "AvD_urban_IHME_UHC80": "Availability Deficit (AvD) for urban population\nas per IHME UHC80 norms",
    "AvD_urban_IHME_UHC90": "Availability Deficit (AvD) for urban population\nas per IHME UHC90 norms",
    "AvD_urban_IPHS": "Availability Deficit (AvD) for urban population\nas per IPHS norms",
    "AvD_urban_MDG": "Availability Deficit (AvD) for urban population\nas per MDG norms",
    "AvD_urban_SDG": "Availability Deficit (AvD) for urban population\nas per SDG norms",
    "AvD_urban_UHC_80": "Availability Deficit (AvD) for urban population\nas per UHC80 norms",
    "AvD_urban_UHC_90": "Availability Deficit (AvD) for urban population\nas per UHC90 norms",
}

VARIABLE_GROUPS = {
    "ApD": [
        "ApD_cadre_mix_Bhore",
        "ApD_cadre_mix_HLEG",
        "ApD_cadre_mix_IHME_UHC80",
        "ApD_cadre_mix_IHME_UHC90",
        "ApD_cadre_mix_IPHS",
        "ApD_sex_mix",
    ],
    "AsD": [
        "AsD",
    ],
    "QD": [
        "QD",
    ],
    "AvD": [
        "AvD_Bhore",
        "AvD_HLEG",
        "AvD_IHME_UHC80",
        "AvD_IHME_UHC90",
        "AvD_IPHS",
        "AvD_MDG",
        "AvD_SDG",
        "AvD_male_Bhore",
        "AvD_male_HLEG",
        "AvD_male_HME_UHC80",
        "AvD_male_IHME_UHC80",
        "AvD_male_IHME_UHC90",
        "AvD_male_IPHS",
        "AvD_male_MDG",
        "AvD_male_SDG",
        "AvD_male_UHC_80",
        "AvD_male_UHC_90",
        "AvD_urban_Bhore",
        "AvD_urban_HLEG",
        "AvD_urban_HME_UHC80",
        "AvD_urban_IHME_UHC80",
        "AvD_urban_IHME_UHC90",
        "AvD_urban_IPHS",
        "AvD_urban_MDG",
        "AvD_urban_SDG",
        "AvD_urban_UHC_80",
        "AvD_urban_UHC_90",
    ],
}

VARIABLE_GROUP_LABELS = {
    "ApD": "Acceptability Deficit (ApD)",
    "AsD": "Accessibility Deficit (AsD)",
    "QD": "Quality Deficit (QD)",
    "AvD": "Availability Deficit (AvD)",
}

# Cadres of interest for the plots
CADRES_OF_INTEREST = (
    "nurse",
    "dentist",
    "pharmacist",
    "anm",
    "ayush",
    "doctor",
    "skilled health professionals",
)

# Mapping of state names to abbreviations
STATE_ABBR = {
    "andhra pradesh": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CG",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jammu & kashmir": "JK",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OR",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN",
    "tripura": "TR",
    "uttarakhand": "UK",
    "uttar pradesh": "UP",
    "west bengal": "WB",
    "andaman & nicobar islands": "AN",
    "chandigarh": "CH",
    "dadra & nagar haveli": "DH",
    "daman and diu": "DD",
    "n.c.t. of delhi": "DL",
    "lakshadweep": "LD",
    "puducherry": "PY",
}

PROJECTION_YEAR = 2021
