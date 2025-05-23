#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:23:38 2025

@author: panosgtzouras
"""

def mapping(df, x, path):
    
    os.chdir(os.path.join(path, 'mappings'))

    

    


    
    elif x == "income":
        mapping2 = {999:999}
        mapping1  = {
            '1: σημαντικά κάτω από το μέσο όρο\xa0': 1,
            '1 (Deutlich unter dem Durchschnitt)': 1,
            'aanzienlijk lager dan het gemiddelde': 1,
            '1.0': 1,
            '1': 1,
        
            '2.0': 2,
            '2': 2,
        
            '3.0': 3,
            '3': 3,
        
            '4.0': 4,
            '4': 4,
        
            '5.0': 5,
            '5': 5,
        
            '6: σημαντικά πάνω από τον μέσο όρο\xa0': 6,
            '6 (Deutlich über dem Durchschnitt)': 6,
            'aanzienlijk hoger dan het gemiddelde': 6,
            '6.0': 6,
            '6': 6,
        
            'Möchte ich nicht angeben': np.nan,
            
            '1: Muito abaixo da média': 1,  # Much below average
            'Over 1.000.001': 6,  # Over 1,000,001 (High income)
            '900.001 - 1.000.000': 6,  # 900,001 - 1,000,000
            '800.001 - 900.000': 5,  # 800,001 - 900,000
            '700.001 - 800.000': 5,  # 700,001 - 800,000
            '600.001 - 700.000': 4,  # 600,001 - 700,000
            '500.001 - 600.000 ': 4,  # 500,001 - 600,000
            '400.001 - 500.000': 3,  # 400,001 - 500,000
            'Under 200.000': 1,  # Below 200,000 (Low income)
            '300.001 - 400.000': 3,  # 300,001 - 400,000
            'Velger å ikke svare': np.nan,  # Prefer not to answer
            '6: Muito acima da média': 6,  # Much above average
        }


    else:
        mapping1 = {999:999}
        mapping2 = {999:999}
    
    return mapping1, mapping2
# %%
import numpy as np
import os
import pandas as pd

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/mappings"



def varMapSave(var, mapping1 = None, mapping2 = None):
    if mapping1 is not None:
        df_map1 = pd.DataFrame(list(mapping1.items()), columns=['original', 'translated'])
        df_map1.to_csv(os.path.join(root_dir, f'{var}_mapping1.csv'), index=False)
    
    if mapping2 is not None:
        df_map2 = pd.DataFrame(list(mapping2.items()), columns=['original', 'translated'])
        df_map2.to_csv(os.path.join(root_dir, f'{var}_mapping2.csv'), index=False)


mapping2 = {999:999}
mapping1 = {
            # Active workers (employees, freelancers, entrepreneurs)
            'Ελεύθερος επαγγελματίας-Επιχειρηματίας': 'active',
            'Freelancer*in oder Unternehmer*in': 'active',
            'zzp’er of ondernemer': 'active',
            'Freelancer or Entrepreneur': 'active',
            'przedsiebiorca': 'active',
            
            'Δημόσιος-Ιδιωτικός υπάλληλος': 'active',
            'Angestellte*r des öffentlichen oder privaten Dienstes': 'active',
            'werknemer in de publieke of private sector': 'active',
            'Public or Private sector employee': 'active',
            'pracownik': 'active',
            
            'Pfleger*in, Handwerker*in, Bau- oder Fabrikarbeiter*in': 'active',
            'conciërge,vakman, werknemer in de bouw of fabriek enz': 'active',
            'Caretaker, craftsman, construction or factory worker, etc.': 'active',
            'robotnik': 'active',
        
            'Αγρότης-Κτηνοτρόφος': 'active',
            'agrariër': 'active',
            'rolnik': 'active',
        
            # Inactive (housekeepers, homemakers, nannies, etc.)
            'Οικιακά': 'inactive',
            'Hausfrau/Hausmann': 'inactive',
            'hulp in de huishouding, kinderoppas, enz.': 'inactive',
            'Housekeeper, maid, nanny, etc.': 'inactive',
            'gosposia': 'inactive',
        
            # Retired
            'Συνταξιούχος': 'retired',
            'gepensioneerd': 'retired',
            'Retire': 'retired',
            'emeryt': 'retired',
        
            # Unemployed
            'Άνεργη/ος': 'unemployed',
            'Arbeitslos': 'unemployed',
            'werkloos': 'unemployed',
            'Unemployed': 'unemployed',
            'bezrobotny': 'unemployed',
        
            # Student
            'Μαθήτρια/ής – Φοιτήτρια/ής': 'student',
            'Μαθήτρια/ής – Φοιτήτρια/ής ': 'student',
            'Student*in': 'student',
            'student': 'student',
            'Student': 'student',
        
            # None (Prefer not to say)
            'Δεν απαντώ': np.nan,
            'Möchte ich nicht angeben': np.nan,
            'zeg ik liever niet': np.nan,
            'Prefer not to say': np.nan,
            'wolenie': np.nan,
            
            # Active workers (employees, freelancers, entrepreneurs)
            'Offentlig sektor': 'active',
            'Privat sektor': 'active',
            'Trabalhador/a por conta de outrém': 'active',  # Employee
            'Trabalhador/a por conta própria': 'active',    # Freelancer
            'Håndverk, bygg og industri': 'active',         # Craftsman, construction, and industry
            
            # Inactive (housekeepers, homemakers, nannies, etc.)
            'Hjemmeværende': 'inactive',  # Homemaker
            'Empregado/a doméstico/a, ama, etc.': 'inactive',  # Housekeeper, maid, nanny, etc.
            'Cuidador/a, artesão/ã, trabalhador/a da construção ou fabril, etc.': 'active',
            
            # Retired
            'Pensjonist': 'retired',    # Retired
            'Reformado/a': 'retired',   # Retired
            'Retiree': 'retired',       # Retired
            
            # Unemployed
            'Arbeidsledig': 'unemployed',  # Unemployed
            'Desempregado/a': 'unemployed',  # Unemployed
            
            # Student
            'Estudante': 'student',  # Student
            
            # None (Prefer not to say)
            'Velger å ikke svare': np.nan,
            'Prefiro não indicar': np.nan, 
        }


    elif x == "income":
        mapping2 = {999:999}
        mapping1  = {
            '1: σημαντικά κάτω από το μέσο όρο\xa0': 1,
            '1 (Deutlich unter dem Durchschnitt)': 1,
            'aanzienlijk lager dan het gemiddelde': 1,
            '1.0': 1,
            '1': 1,
        
            '2.0': 2,
            '2': 2,
        
            '3.0': 3,
            '3': 3,
        
            '4.0': 4,
            '4': 4,
        
            '5.0': 5,
            '5': 5,
        
            '6: σημαντικά πάνω από τον μέσο όρο\xa0': 6,
            '6 (Deutlich über dem Durchschnitt)': 6,
            'aanzienlijk hoger dan het gemiddelde': 6,
            '6.0': 6,
            '6': 6,
        
            'Möchte ich nicht angeben': np.nan,
            
            '1: Muito abaixo da média': 1,  # Much below average
            'Over 1.000.001': 6,  # Over 1,000,001 (High income)
            '900.001 - 1.000.000': 6,  # 900,001 - 1,000,000
            '800.001 - 900.000': 5,  # 800,001 - 900,000
            '700.001 - 800.000': 5,  # 700,001 - 800,000
            '600.001 - 700.000': 4,  # 600,001 - 700,000
            '500.001 - 600.000 ': 4,  # 500,001 - 600,000
            '400.001 - 500.000': 3,  # 400,001 - 500,000
            'Under 200.000': 1,  # Below 200,000 (Low income)
            '300.001 - 400.000': 3,  # 300,001 - 400,000
            'Velger å ikke svare': np.nan,  # Prefer not to answer
            '6: Muito acima da média': 6,  # Much above average
        }


varMapSave('income', mapping1 = mapping1, mapping2 = mapping2)

# %%

path = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"

def mapping(df, x, path):
    os.chdir(os.path.join(path, 'mappings'))

    def load_mapping(file_prefix):
        df_map = pd.read_csv(f'{file_prefix}_mapping1.csv')
        mapping1 = dict(zip(df_map['original'], df_map['translated']))
        df_map = pd.read_csv(f'{file_prefix}_mapping2.csv')
        mapping2 = dict(zip(df_map['original'], df_map['translated']))
        return mapping1, mapping2

    group_simple = {'afford', 'mode', 'purp', 'gender', 'age', 'educ', 'employ', 'income'}
    group_time = {
        "nonpeakCar", "nonpeakTaxi", "nonpeakPT", "nonpeakMoto", "nonpeakBike", "nonpeakWalk",
        "peakCar", "peakTaxi", "peakPT", "peakMoto", "peakBike", "peakWalk",
        'walkBus', 'walkTrain', 'waitBus', 'waitTrain'
    }
    group_safety = {
        'perSafeCar', 'perSafeTaxi', 'perSafePT', 'perSafeMoto', 'perSafeBike', 'perSafeWalk',
        'psafeCar', 'psafeTaxi', 'psafePT', 'psafeMoto', 'psafeBike', 'psafeWalk',
        'accept', 'satisfy', 'reliable'
    }

    if x in group_simple:
        return load_mapping(x)
    elif x in group_time:
        mapping1 = mappingTimes(df, x)
        mapping2 = dict(zip(pd.read_csv('time_interval_mapping2.csv')['original'],
                            pd.read_csv('time_interval_mapping2.csv')['translated']))
    elif x in group_safety:
        mapping1 = mappingRate(df, x)
        mapping2 = dict(zip(pd.read_csv('safety_interval_mapping2.csv')['original'],
                            pd.read_csv('safety_interval_mapping2.csv')['translated']))
    else:
        mapping1 = mapping2 = {999: 999}

    return mapping1, mapping2

