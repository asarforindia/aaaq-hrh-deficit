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
            when education = '00' then 'Not literate'
            when education = '01' then 'literate without formal schooling'
            when education = '02' then 'Literate but below primary.'
            when education = '03' then 'Primary.'
            when education = '04' then 'Middle'
            when education = '05' then 'Secondary.'
            when education = '06' then 'Graduate and above in: Agriculture.'
            when education = '07' then 'Graduate and above in: engineering/technology'
            when education = '08' then 'Graduate and above in: Medicine.'
            when education = '09' then 'Graduate and above in: Other subjects.'
            else NULL
        end
    );

create temporary function technical_education(education string)
    returns string as (
        case
            when education = '10' then 'Additional diploma/certificate: agriculture.'
            when education = '11' then 'Additional diploma/certificate: Engineering/technology.'
            when education = '12' then 'Additional diploma/certificate: Medicine.'
            when education = '13' then 'Additional diploma/certificate: Crafts.'
            when education = '14' then 'Additional diploma/certificate: Other subjects.'
            else NULL
        end
    );

create temporary function is_qualified(occupation string, education string, technical string)
    returns int64 as (
        case
            when occupation in ('Doctor', 'Dentist', 'AYUSH') and (
                education = 'Graduate and above in: Medicine.' or (
                    education = 'Secondary.' and 
                    technical = 'Additional diploma/certificate: Medicine.'
                )
            ) then 1
            when occupation in ('Nurse', 'ANM') and (
                education = 'Graduate and above in: Medicine.' or (
                    education = 'Secondary.' and 
                    technical = 'Additional diploma/certificate: Medicine.'
                )
            ) then 1
            when occupation = 'Pharmacist' and (
                education in (
                    'Graduate and above in: engineering/technology',
                    'Graduate and above in: Medicine.',
                    'Graduate and above in: Other subjects.'
                ) or (
                    education = 'Secondary.' and
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
    workers_38 as (
        select
            occupation_nco_1968(B6_q6) as primary_occupation,
            occupation_nco_1968(B6_q11) as secondary_occupation,
            educational_attainment(B41_q8) as education,
            technical_education(B41_q9) as technical,
            ifnull(
                occupation_nco_1968(B6_q6),
                occupation_nco_1968(B6_q11)
            ) as occupation,
            is_qualified(
                ifnull(
                    occupation_nco_1968(B6_q6),
                    occupation_nco_1968(B6_q11)
                ),
                educational_attainment(B41_q8),
                technical_education(B41_q9)
            ) as is_qualified_,
            b6.Hhold_key as hhid,
            b6.Wgt4_pooled as weight_,
            b6.State AS state_
        from 
            `asar-287123.nss.nss_38_block_6` as b6
        left outer join 
            `asar-287123.nss.nss_38_block_41` as b41
        on
            b6.Person_key = b41.Person_key
    ),

    households_38 as (
        select 
            hhid,
            occupation,
            count(occupation) as count_,
            sum(workers_38.is_qualified_) as qualified_count,
            any_value(weight_) as weight_,
            any_value(state_) as state_
        from 
            workers_38 
        where 
            occupation != 'Other'
        group by 
            hhid,
            occupation
    ),

    estimates_38 as (
        select 
            state_,
            occupation,
            sum(count_ * weight_) as population_,
            sum(households_38.qualified_count * households_38.weight_) as qualified_population
        from 
            households_38 
        group by
            state_,
            occupation
    )

select
    *
from
    estimates_38
order by
    occupation
