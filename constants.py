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
    "nurse": "Nurses",
    "dentist": "Dentists",
    "pharmacist": "Pharmacists",
    "anm": "ANMs",
    "ayush": "AYUSH",
    "doctor": "Doctors",
    "skilled health professionals": "Skilled Health Professionals",
    "nursing cadres": "Nursing Cadres",
    "supporting cadres": "Supporting Cadres (Nurses, Pharmacists, etc.)",
    "all cadres": "All Cadres",
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
}

VARIABLE_GROUPS = {
    "ApD_cadre_mix": [
        "ApD_cadre_mix_Bhore",
        "ApD_cadre_mix_HLEG",
        "ApD_cadre_mix_IHME_UHC80",
        "ApD_cadre_mix_IHME_UHC90",
        "ApD_cadre_mix_IPHS",
    ],
    "ApD_sex_mix": [
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
    ],
}

THRESHOLD_GROUPS = {
    "Bhore": {
        "ApD_cadre_mix": "ApD_cadre_mix_Bhore",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_Bhore",
    },
    "HLEG": {
        "ApD_cadre_mix": "ApD_cadre_mix_HLEG",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_HLEG",
    },
    "IHME_UHC80": {
        "ApD_cadre_mix": "ApD_cadre_mix_IHME_UHC80",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_IHME_UHC80",
    },
    "IHME_UHC90": {
        "ApD_cadre_mix": "ApD_cadre_mix_IHME_UHC90",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_IHME_UHC90",
    },
    "IPHS": {
        "ApD_cadre_mix": "ApD_cadre_mix_IPHS",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_IPHS",
    },
    "MDG": {
        "ApD_cadre_mix": "ApD_cadre_mix_MDG",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_MDG",
    },
    "SDG": {
        "ApD_cadre_mix": "ApD_cadre_mix_SDG",
        "ApD_sex_mix": "ApD_sex_mix",
        "AsD": "AsD",
        "QD": "QD",
        "AvD": "AvD_SDG",
    },
}

VARIABLE_GROUP_LABELS = {
    "ApD_cadre_mix": "Acceptability Deficit Cadre-Mix (ApD Cadre-Mix)",
    "ApD_sex_mix": "Acceptability Deficit Sex-Mix (ApD Sex-Mix)",
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

STATE_IDS = [
    "arunachal pradesh",
    "assam",
    "chandigarh",
    "karnataka",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "punjab",
    "rajasthan",
    "sikkim",
    "tripura",
    "uttarakhand",
    "bihar",
    "kerala",
    "madhya pradesh",
    "gujarat",
    "lakshadweep",
    "odisha",
    "jammu & kashmir",
    "chhattisgarh",
    "goa",
    "haryana",
    "himachal pradesh",
    "jharkhand",
    "tamil nadu",
    "uttar pradesh",
    "west bengal",
    "andhra pradesh",
    "puducherry",
    "maharashtra",
    "n.c.t. of delhi",
    "andaman & nicobar islands",
    "dadra & nagar haveli",
]

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

AVD_DEF = """
## Availability deficit (AvD)

Availability deficit measures the gap between available HRH and context-specific requirement thresholds, 
ranging theoretically from +1 to –∞. In this plot, all surplus values (AvD < 0) are capped at -1 to maintain focus on positive deficit values, 
as large negative values can distort the visualization. 
AvD equals 0 when there is no deficit, takes values >0 to ≤1 when a deficit exists, and is negative when there is a surplus.
"""

ASD_DEF = """
## Accessibility Deficit

Accessibility deficit (AsD) measures the deficit of HRH present in rural areas relative to their urban counterparts, 
ranging theoretically from +1 to –∞. In this plot, all surplus values (AsD < 0) are capped at -1 to maintain focus on positive deficit values, 
as large negative values can distort the visualization.
AsD equals 0 when there is no deficit, takes values >0 to ≤1 when a deficit exists, and is negative when there is a surplus.
"""

APD_SEX_MIX_DEF = """
## Acceptability Deficit (sex-mix)

Acceptability deficit sex-mix (ApD sex-mix) measures the imbalance of female personnel relative to males for a cadre, 
ranging theoretically from +1 to –∞. In this plot, all surplus values (ApDsex-mix < 0) are capped at -1 to maintain 
focus on positive deficit values, as large negative values can distort the visualization.
ApDsex-mix equals 0 when there is no deficit, takes values >0 to ≤1 when a deficit exists, and is negative when there is a surplus.
"""

APD_CADRE_MIX_DEF = """
## Acceptability Deficit (cadre-mix)

Acceptability deficit cadre-mix (ApD cadre-mix) measures the proportion of relatively available nursing or supporting cadres to relatively available doctors, 
where relative availability is defined as the available HRH density of a cadre divided by its requirement threshold. 
It can theoretically range from +1 to –∞. 
In this plot, all surplus values (ApD cadre-mix < 0) are capped at -1 to maintain focus on positive deficit values, 
as large negative values can distort the visualization. ApDcadre-mix equals 0 when there is no deficit, 
takes values >0 to ≤1 when a deficit exists, and is negative when there is a surplus.
"""

QD_DEF = """
## Quality Deficit

Quality Deficit (QD) measures the paucity of skilled professionals in relation to total HRH i.e, qualified and unqualified. 
Theoretically, QD can range from 0 to +1. A zero value depicts an adequate number of HRH, 
while a non-existence of any skilled HRH depicts a +1 value for QD.
"""

VARIABLE_GROUP_DEFS = {
    "ApD_cadre_mix": APD_CADRE_MIX_DEF,
    "ApD_sex_mix": APD_SEX_MIX_DEF,
    "AsD": ASD_DEF,
    "QD": QD_DEF,
    "AvD": AVD_DEF,
}

THRESHOLD_DEFS = """
Definitions of norms used in the plots:

* **Bhore:** HRH requirement thresholds recommended by the Bhore Committee, the first national health committee in India.
* **IPHS:** HRH requirement thresholds outlined in the Indian Public Health Standards, focusing on staffing for the public health system.
* **HLEG:** HRH requirement thresholds recommended by the High-Level Expert Group on Universal Health Coverage, the most recent national report with HRH guidance.
* **IHME UHC80:** HRH requirement thresholds estimated by IHME for achieving a Universal Health Coverage (UHC) service coverage index of 80.
* **IHME UHC90:** HRH requirement thresholds estimated by IHME for achieving a UHC service coverage index of 90.
* **SDG:** Skilled health professional thresholds recommended by WHO to meet Sustainable Development Goal targets.
* **MDG:** Skilled health professional thresholds recommended by WHO to meet Millennium Development Goal targets.
"""
