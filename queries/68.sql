create temp function occupation_code(nco string, nic string)
    returns string as (
        case
            when nco = '222' and nic = '86201' then 'Doctor'
            when nco = '222' and nic = '86202' then 'Dentist' 
            when nco = '222' and nic >= '86901' and nic <= '86903' then	'AYUSH'
            when nco = '222' and nic >= '86904' and nic <= '86909' then	'Doctor'
            when nco = '223' and nic = '87100' then	'Nurse'
            when nco = '222' and nic >= '86901' and nic <= '86903' then	'AYUSH'
            when nco = '222' and nic >= '86904' and nic <= '86909' then	'Doctor'
            when nco in ('323') and nic >= '86100' and nic <= '86909' then 'ANM'
            when nco in ('222', '223', '322', '323') and nic >= '87100' and nic <= '87900' then 'Nurse'
            when nco in ('322', '324') and nic >= '86100' and nic <= '86909' then 'ANM'
            when nco in ('322', '324') and nic >= '87100' and nic <= '87900' then 'ANM'
            when nco in ('211', '221', '323', '324') and nic = '47721' then 'Pharmacist'
            else NULL
        end
    );

create temporary function technical_education(education string)
    returns string as (
        case
            when education = '01' then 'No technical education'
            when education = '02' then 'Technical degree in agriculture/ engineering/ technology/  medicine, etc'
            when education = '03' then 'Diploma or certificate (below graduate level) in:   Agriculture'
            when education = '04' then 'Diploma or certificate (below graduate level) in:   Engineering/   technology'
            when education = '05' then 'Diploma or certificate (below graduate level) in:   Medicine'
            when education = '06' then 'Diploma or certificate (below graduate level) in:   Crafts'
            when education = '07' then 'Diploma or certificate (below graduate level) in:   Other subjects'
            when education = '08' then 'Diploma or certificate (graduate and above level) in:  Agriculture'
            when education = '09' then 'Diploma or certificate (graduate and above level) in:  Engineering/ technology'
            when education = '10' then 'Diploma or certificate (graduate and above level) in:  Medicine'
            when education = '11' then 'Diploma or certificate (graduate and above level) in:  Crafts'
            when education = '12' then 'Diploma or certificate (graduate and above level) in:  Other subjects'
            else NULL
        end
    );

create temporary function is_qualified(occupation string, technical string)
    returns int64 as (
        case
            when occupation in ('Doctor', 'Dentist', 'AYUSH', 'Doctor, Dentist, AYUSH') and (
                technical in (
                    'Diploma or certificate (below graduate level) in:   Medicine',
                    'Diploma or certificate (graduate and above level) in:  Medicine'
                )
            ) then 1
            when occupation in ('Nurse', 'ANM') and (
                technical in (
                    'Diploma or certificate (below graduate level) in:   Medicine',
                    'Diploma or certificate (graduate and above level) in:  Medicine'
                )
            ) then 1
            when occupation = 'Pharmacist' and (
                technical in (
                    'Diploma or certificate (below graduate level) in:   Engineering/   technology',
                    'Diploma or certificate (below graduate level) in:   Medicine',
                    'Diploma or certificate (below graduate level) in:   Other subjects',
                    'Diploma or certificate (graduate and above level) in:  Agriculture',
                    'Diploma or certificate (graduate and above level) in:  Engineering/ technology',
                    'Diploma or certificate (graduate and above level) in:  Medicine',
                    'Diploma or certificate (graduate and above level) in:  Other subjects'
                )
            ) then 1
            when occupation is NULL then NULL
            else 0
        end
    );

with
    workers_main_68 as (
        select
            -- We had to reverese the names becaues they're already
            --  reveresed in the original data
            Person_Serial_No,
            HHID as hhid,

            occupation_code(
                Usual_Principal_Activity_NCO2004, 
                Usual_Principal_Activity_NIC2008
            ) as occupation,
            
            Multiplier_comb as weight_,
            State as state_
        from
            `asar-287123.nss.nss_68_block_51`
    ),

    workers_sub_68 as (
        select
            Person_Serial_No,
            HHID as hhid,
            -- the max would work because we are eliminating all
            -- non-medical occupations. conflict would happen only
            -- if the person has multiple medical occupations
            max(occupation_code(
                Usual_SubsidiaryActivity_NCO2004, Usual_SubsidiaryActivity_NIC2004
            )) as occupation,
        from
            `asar-287123.nss.nss_68_block_52`
        group by
            Person_Serial_No,
            HHID
    ),

    workers_edu_68 as (
        select
            Person_Serial_No,
            HHID as hhid,
            technical_education(Technical_Education) as technical,
        from
            `asar-287123.nss.nss_68_block_4`
    ),
    
    workers_68 as (
        select
            b51.occupation as primary_occupation,
            b52.occupation as secondary_occupation,
            technical,

            ifnull(b51.occupation, b52.occupation) as occupation,
            is_qualified(
                ifnull(b51.occupation, b52.occupation), technical
            ) as is_qualified_,

            b51.hhid,
            b51.weight_,
            b51.state_
        from
            workers_main_68 as b51
        left outer join
            workers_sub_68 as b52
        on
            b51.Person_Serial_No = b52.Person_Serial_No and b51.hhid = b52.hhid
        left outer join
            workers_edu_68 as b4
        on
            b51.Person_Serial_No = b4.Person_Serial_No and b51.hhid = b4.hhid
    ),

    households_68 as (
        select 
            hhid,
            occupation,
            count(occupation) as count_,
            sum(is_qualified_) as qualified_count,
            any_value(weight_) as weight_,
            any_value(state_) as state_
        from 
            workers_68
        where 
            occupation != 'Other'
        group by 
            hhid,
            occupation
    ),

    estimates_68 as (
        select 
            state_,
            occupation,
            sum(count_ * weight_) as population_,
            sum(qualified_count * weight_) as qualified_population
        from 
            households_68
        group by
            state_,
            occupation
    )

select
    *
from
    estimates_68
order by
    occupation
