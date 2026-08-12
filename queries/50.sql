create temp function occupation_nco_1968(nco string)
    returns string as (
        case
            when nco = '085' then 'ANM'
            when nco = '084' then 'Nurse'
            when nco = '076' then 'Pharmacist'
            when nco = '083' then 'Pharmacist'
            when nco = '070' then 'Doctor'
            when nco = '078' then 'Doctor'
            when nco = '079' then 'Doctor'
            when nco = '074' then 'Dentist'
            when nco = '081' then 'Dentist'
            when nco = '071' then 'AYUSH'
            when nco = '072' then 'AYUSH'
            when nco = '073' then 'AYUSH'
            else NULL
        end
    );


create temporary function educational_attainment(education string)
    returns string as (
        case
            when education = '01' then 'Not literate'
            when education = '02' then 'Literate through attending : NFEC/AEC'
            when education = '03' then 'TLC'
            when education = '04' then 'Others'
            when education = '05' then 'Literate but below primary'
            when education = '06' then 'Primary.'
            when education = '07' then 'Middle'
            when education = '08' then 'Secondary.'
            when education = '09' then 'Higher secondary'
            when education = '10' then 'Graduate and above in: Agriculture.'
            when education = '11' then 'Graduate and above in: engineering/technology'
            when education = '12' then 'Graduate and above in: Medicine.'
            when education = '13' then 'Graduate and above in: Other subjects.'
            else NULL
        end
    );


create temporary function technical_education(education string)
    returns string as (
        case
            when education = '1' then 'No technical education'
            when education = '2' then 'Additional diploma/certificate: agriculture.'
            when education = '3' then 'Additional diploma/certificate: Engineering/technology.'
            when education = '4' then 'Additional diploma/certificate: Medicine.'
            when education = '5' then 'Additional diploma/certificate: Crafts.'
            when education = '9' then 'Additional diploma/certificate: Other subjects.'
            else NULL
        end
    );

create temporary function is_qualified(occupation string, education string, technical string)
    returns int64 as (
        case
            when occupation in ('Doctor', 'Dentist', 'AYUSH') and (
                education = 'Graduate and above in: Medicine.' or (
                    education in ('Secondary.', 'Higher secondary') and 
                    technical = 'Additional diploma/certificate: Medicine.'
                )
            ) then 1
            when occupation in ('Nurse', 'ANM') and (
                education = 'Graduate and above in: Medicine.' or (
                    education in ('Secondary.', 'Higher secondary') and 
                    technical = 'Additional diploma/certificate: Medicine.'
                )
            ) then 1
            when occupation = 'Pharmacist' and (
                education in (
                    'Graduate and above in: engineering/technology',
                    'Graduate and above in: Medicine.',
                    'Graduate and above in: Other subjects.'
                ) or (
                    education in ('Secondary.', 'Higher secondary') and
                    technical in (
                        'Additional diploma/certificate: Engineering/technology.',
                        'Additional diploma/certificate: Medicine.',
                        'Additional diploma/certificate: Other subjects.'
                    )
                )
            ) then 1
            when occupation is NULL then NULL
            else 0
        end
    );


with
    workers_50 as (
        select
            occupation_nco_1968(B4_q15) as primary_occupation,
            occupation_nco_1968(B4_q21) as secondary_occupation,
            educational_attainment(B4_q7) as education,
            technical_education(B4_q8) as technical,
            ifnull(
                occupation_nco_1968(B4_q15),
                occupation_nco_1968(B4_q21)
            ) as occupation,
            is_qualified(
                ifnull(
                    occupation_nco_1968(B4_q15),
                    occupation_nco_1968(B4_q21)
                ),
                educational_attainment(B4_q7),
                technical_education(B4_q8)
            ) as is_qualified_,
            b4.Hhold_key AS hhid,
            b4.WGT_POOLED AS weight_,
            b4.State AS state_
        from 
            `asar-287123.nss.nss_50_block_4` as b4
    ),

    households_50 as (
        select 
            hhid,
            occupation,
            count(occupation) as count_,
            sum(workers_50.is_qualified_) as qualified_count,
            any_value(weight_) as weight_,
            any_value(state_) as state_
        from 
            workers_50
        where 
            occupation != 'Other'
        group by 
            hhid,
            occupation
    ),

    estimates_50 as (
        select 
            state_,
            occupation,
            sum(count_ * weight_) as population_,
            sum(households_50.qualified_count * households_50.weight_) as qualified_population
        from 
            households_50
        group by
            state_,
            occupation
    )

select
    *
from
    estimates_50
order by
    occupation
