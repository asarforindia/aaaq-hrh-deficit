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
            when education = '2' then 'Technical degree in agriculture / engineering / technology / medicine etc.'
            when education = '3' then 'Additional diploma/certificate: agriculture.'
            when education = '4' then 'Additional diploma/certificate: Engineering/technology.'
            when education = '5' then 'Additional diploma/certificate: Medicine.'
            when education = '6' then 'Additional diploma/certificate: Crafts.'
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
                    technical in (
                        'Additional diploma/certificate: Medicine.',
                        'Technical degree in agriculture / engineering / technology / medicine etc.'
                    )
                )
            ) then 1
            when occupation in ('Nurse', 'ANM') and (
                education = 'Graduate and above in: Medicine.' or (
                    education in ('Secondary.', 'Higher secondary') and 
                    technical in (
                        'Additional diploma/certificate: Medicine.',
                        'Technical degree in agriculture / engineering / technology / medicine etc.'
                    )
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
                        'Additional diploma/certificate: Other subjects.',
                        'Technical degree in agriculture / engineering / technology / medicine etc.'
                    )
                )
            ) then 1
            when occupation is NULL then NULL
            else 0
        end
    );


with
    workers_main_55 as (
        select
            -- We had to reverese the names becaues they're already
            --  reveresed in the original data
            Key_prsn,
            Key_Hhold as hhid,

            occupation_nco_1968(B51_q6) as occupation,
            Wgt_10_10_1_SR_comb as weight_,
            State as state_
        from
            `asar-287123.nss.nss_55_block_512`
    ),

    workers_sub_55 as (
        select
            Key_prsn,
            -- the max would work because we are eliminating all
            -- non-medical occupations. conflict would happen only
            -- if the person has multiple medical occupations
            max(occupation_nco_1968(B52_q6)) as occupation,
        from
            `asar-287123.nss.nss_55_block_521`
        group by
            Key_prsn

        union all

        select
            Key_prsn,
            -- the max would work because we are eliminating all
            -- non-medical occupations. conflict would happen only
            -- if the person has multiple medical occupations
            max(occupation_nco_1968(B52_q6)) as occupation,
        from
            `asar-287123.nss.nss_55_block_522`
        group by
            Key_prsn
    ),

    workers_edu_55 as (
        select
            Key_prsn,
            educational_attainment(B4_q7) as education,
            technical_education(B4_q8) as technical,
        from
            `asar-287123.nss.nss_55_block_41`
    ),
    
    workers_55 as (
        select
            b51.occupation as primary_occupation,
            b52.occupation as secondary_occupation,
            education,
            technical,

            ifnull(b51.occupation, b52.occupation) as occupation,
            is_qualified(
                ifnull(b51.occupation, b52.occupation), education, technical
            ) as is_qualified_,

            b51.hhid,
            b51.weight_,
            b51.state_
        from
            workers_main_55 as b51
        left outer join
            workers_sub_55 as b52
        on
            b51.Key_prsn = b52.Key_prsn
        left outer join
            workers_edu_55 as b4
        on
            b51.Key_prsn = b4.Key_prsn
    ),

    households_55 as (
        select 
            hhid,
            occupation,
            count(occupation) as count_,
            sum(is_qualified_) as qualified_count,
            any_value(weight_) as weight_,
            any_value(state_) as state_
        from 
            workers_55
        where 
            occupation != 'Other'
        group by 
            hhid,
            occupation
    ),

    estimates_55 as (
        select 
            state_,
            occupation,
            sum(count_ * weight_) as population_,
            sum(qualified_count * weight_) as qualified_population
        from 
            households_55
        group by
            state_,
            occupation
    )

select
    *
from
    estimates_55
order by
    occupation
