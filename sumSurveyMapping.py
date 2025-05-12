import numpy as np
import pandas as pd
import re

# "gdf.afford.unique()
# Out[282]: 
# array([nan, 'Meer dan 50%', '10-20%', '20-30%', '0-10%', '30-40%',
#       '0 bis 10%', '20 bis 30%', '10 bis 20%', '30 bis 40%',
#       '40 bis 50%', 'Mehr als 50%', '20 - 30%', '0 - 10%', '10 - 20%',
#       '40 - 50%', '30 - 40%'], dtype=object) 
# "  These are the unique values, 
#I want a code to replace and group them in python in the following categories: 
    #[0-10%, 10-20%, 20-30%, 30-40%, more than 50%]. GIVE ME TH MAPPING.

# gdf.nonpeakCar.unique()
# Out[291]: 
# array([nan, '80 - 90', '70 - 80', '1 - 10', 'weet niet', '30 - 40',
#       '10 - 20', 'meer dan 90', '20 - 30', '40 - 50', '50 - 60',
#       '60 - 70', '20 bis 30', '1 bis 10', '30 bis 40', '10 bis 20',
#       'ich weiß nicht', 'mehr als 50', '40 bis 50', '15-30', '1-15',
#       '60-75', 'Περισσότερο από 90 λεπτά', '45-60', '30-45', '15-Jan'],
#      dtype=object) THESE ARE THE UNIQUE VALUES, EACH I WANT TO REPLACE WITH MEDIAN VALUES OF THESE INTERVALS

def extract_numbers(text):
    if isinstance(text, str):
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
    return None


def mappingRate(df, x):
    data = df[x]
    data = [np.nan if val == 'nan' else val for val in data]
    df = pd.DataFrame({'original_text': data})
    df['numbers'] = df['original_text'].apply(extract_numbers)
    df = df.dropna(subset=['numbers'])
    df['numbers'] = df['numbers'].astype(int)
    mapping_dict = dict(zip(df['original_text'], df['numbers']))
    # print(mapping_dict)
    return mapping_dict


def mappingTimes(df, x): 
    mapS = df[x].unique()
    pattern = r'(\d+)\s*-\s*(\d+)'
    mins = []
    maxs = []
    meds = []
    match_status = []

    for item in mapS:
        
      if isinstance(item, str):
      
        match = re.search(pattern, item)

        if match: 
            min_value = int(match.group(1))
            mins.append(min_value)
            max_value = int(match.group(2))
            maxs.append(max_value)
            # interval_mapping[item] = (min_value, max_value)
            match_status.append('Matched')
        else:
            mins.append(0)
            maxs.append(999999)
            meds = 0
            match_status.append('Not Matched')
      else:
        mins.append(None)
        maxs.append(None)
        match_status.append(None)

    mapMap = pd.DataFrame({'orig': mapS, 'match': match_status, 'minimum': mins, 
                           'maximum': maxs, 'mediums': meds}).dropna()
    mapMap['meds'] = 0.5 * (mapMap.maximum - mapMap.minimum) + mapMap.minimum
    matched_rows = mapMap[mapMap['match'] == 'Matched']
    mapTimes = dict(zip(matched_rows['orig'], matched_rows['meds']))
    return mapTimes

def mapping(df, x):
    if x == "afford":
        mapping1 = {
            'nan': np.nan,
            'Meer dan 50%': 'More than 50%',
            '0-10%': '0-10%',
            '10-20%': '10-20%',
            '20-30%': '20-30%',
            '30-40%': '30-40%',
            '0 bis 10%': '0-10%',
            '20 bis 30%': '20-30%',
            '10 bis 20%': '10-20%',
            '30 bis 40%': '30-40%',
            '40 bis 50%': '40-50%',
            'Mehr als 50%': 'More than 50%',
            '20 - 30%': '20-30%',
            '0 - 10%': '0-10%',
            '10 - 20%': '10-20%',
            '40 - 50%': '40-50%',
            '30 - 40%': '30-40%',
            '30%-20%': '20-30%',
            '10%-0%': '0-10%',
            '20%-10%': '10-20%',
            '40%-30%': '30-40%',
            'more than 50%': 'More than 50%',
            '50%-40%': '40-50%',
            'Vet ikke/ Ikke relevant': np.nan, 'Mer enn 50%': 'More than 50%',
            'περισσότερο από 50%': 'More than 50%', 'więcej niż 50%': 'More than 50%', ' ':np.nan}
        mapping2 = {'More than 50%':0.50, '10-20%': 0.15, '20-30%': 0.25,
                          '0-10%':0.05, '30-40%':0.35, '40-50%': 0.4, 'mais de 50%': 0.5}
    elif (x == "nonpeakCar" or x == "nonpeakTaxi" or x == "nonpeakPT" or x == "nonpeakMoto" or x == "nonpeakBike" or x == "nonpeakWalk" 
          or x == "peakCar" or x == "peakTaxi" or x == "peakPT" or x == "peakMoto" or x == "peakBike" or x == "peakWalk" or 
          x == 'walkBus' or x == 'walkTrain' or x == 'waitBus' or x == 'waitTrain'): 
        mapping1 = mappingTimes(df, x)
        # print('PASOK')
        mapping2 = {'meer dan 90': 95, '20 bis 30': 25, '1 bis 10': 5, '30 bis 40': 35, '10 bis 20': 15, 
                    'ich weiß nicht': np.nan, 'mehr als 50': 55, '40 bis 50': 45, 'weet niet': np.nan,
                    'Περισσότερο από 90 λεπτά': 95, '15-Jan': 17.5,
                    'meer dan 50 minuten': 55, '0 bis 10': 5, 'nicht zutreffend': np.nan, 'mehr als 50 Minuten': 55,
                    'niet van toepassing': np.nan, 'Περισσότερο από 50 λεπτά': 55,  '20-Oct': 25, '40bis 50': 45,
                    'Μη διαθέσιμο': np.nan, 'Περισσότερο από 25 λεπτά': 30, '10-May': 12.5, '15-Oct': 17.5,
                    'mehr als 25 Min.': 25, 'nie wiem':np.nan, 'ponad 90': 95, 'ponad 50 minut':55, 'Nie dotyczy_':np.nan,
                    'ponad 25 minut': 30, 'Non applicable': np.nan, 'Plus de 50': 55, 'do not know': np.nan,
                    'Vet ikke/ Ikke relevant': np.nan, 'Vet ikke/ ikke relevant':np.nan, 'Vet ikke/Ikke relevant':np.nan,
                    'Mer enn 90 min': 95, 'Mer enn 50 minutter': 55, 'Mer enn 25 min': 30, 1012: 7.5, 8:7.5,
                    'mais de 90': 95, 'Não aplicável': np.nan, 'mais de 50': 55, 1014:np.nan, 1016:np.nan, 1016.5:np.nan, 'Je ne sais pas': np.nan,
                    'Plus que 50': 55, 'Plus que 25': 30, 5.5: 5, 'more than 90': 0.95, 'more than 25 minutes':30, 'Not applicable': np.nan,
                    'Not Applicable':np.nan, 'more than 50 minutes': 50,
                    'more than 25 minutes ': 25,
                    '3':np.nan,'1':np.nan,'2':np.nan,'6':np.nan,'4':np.nan, '5': np.nan,
                    'The transport system in my city offers some multimodal options, but there is room for improvement in connecting them smoothly':np.nan,
                    "My city's transport system is very multimodal, offering seamless integration of various transport modes like buses, trains, cycling, and walking":np.nan,
                    "My city's transport system is not multimodal, primarily relying on singular or isolated modes of transportation.":np.nan,
                    'While there are different transportation modes available in my city, they operate more independently than in an integrated manner.':np.nan,
                    '6 (Very safe)': np.nan,
                    '1 (Not safe at all)':np.nan,
                    'more than 50 minutes ': 50, 0.95:5, 1017:np.nan, 
                    1012.50:np.nan, 0.95: 5}

    elif (x == 'perSafeCar' or x == 'perSafeTaxi' or x == 'perSafePT' or 
           x == 'perSafeMoto' or x == 'perSafeBike'or x == 'perSafeWalk' or x == 'psafeCar'or x == 'psafeTaxi' or
           x == 'psafePT'or x == 'psafeMoto'or x == 'psafeBike'or x == 'psafeWalk'or x == 'accept'or x =='satisfy' or 
           x == 'reliable'):
        
        mapping1 = mappingRate(df, x)
        mapping2 = {'zeer tevreden': 6, 'zeer ontevreden': 1, 'totaal niet acceptabel': 1, 'volledig acceptabel': 6,
                    'zeer betrouwbaar': 6, 'totaal niet betrouwbaar': 1, 'Vet ikke/Ikke relevant': np.nan,
                    '1 (Not safe at all)':1, '6 (Very safe)':6, '6 (Very safe)':6, '1 (Not safe at all)':1}
    
    
    elif (x == 'mode'):
        mapping1 = {
            
            # car
            # taxi
            # train
            # bus
            # motorcycle
            # bicycle
            # escooter
            # walking
            # car sharing
            # micromobility
            # ride hailing
            
            # Original mappings

            'Auto': 'car',
            'bus': 'bus',
            'eigen auto': 'car',
            'eigen (elektrische) fiets': 'bicycle',
            'eigen e-scooter (of ander microvoertuig)': 'escooter',
            'taxi': 'taxi',
            'te voet': 'walking',
            'metro, tram, ondergronds spoor enz.': 'train',
            'eigen motor': 'motorcycle',
            '(elektrische) deelfiets (of e-bike)': 'micromobility',
            'ritbemiddeling of pendeldienst': 'ride hailing',
            'deelauto': 'car sharing',
            'deel-e-scooter (of ander microvoertuig)': 'micromobility',
            'Zu Fuß': 'walking',
            'U-Bahn, Tram, S-Bahn ': 'train',
            'Bus': 'bus',
            'Privates Fahrrad (oder E-Bike)': 'bicycle',
            'Taxi': 'taxi',
            'Privates Motorrad': 'motorcycle',
            'Sharing Mikromobilitätsfahrzeug (E-Tretroller, E-Motorroller, Lastenrad)': 'micromobility',
            'Carsharing-Fahrzeug': 'car sharing',
            'Ridehailing oder Shuttledienst': 'ride hailing',
            'Bikesharing-Fahrrad (oder E-Bike)': 'micromobility',
            'Privates Mikromobilitätsfahrzeug (E-Tretroller, E-Motorroller, Lastenrad)': 'escooter',
            'Elektroauto': 'car',
            '1: Αυτοκίνητο (ιδιωτικό)': 'car',
            '4: Λεωφορείο, Τρόλεϊ': 'bus',
            '0: Περπάτημα': 'walking',
            '3: Μετρό, Τραμ, Προαστιακός': 'train',
            '6: Μοτοσικλέτα (ιδιωτική)': 'motorcycle',
            'deelmotor': 'motorcycle',
            'Bikesharing-Fahrrad ': 'micromobility',
            'Prywatny samoch?d': 'car',
            'Transports publics;': 'train',
            'Metro, tramwaj, kolej podmiejsk': 'train',
            'Marche;Transports publics;': 'train',
            'Autobus': 'bus',
            'Vélo personnel;': 'bicycle',
            'Rower prywatny (lub rower elekt': 'bicycle',
            'Prywatna hulajnoga elektryczna': 'escooter',
            'Marche;': 'walking',
            'Pieszo': 'walking',
            'Buss':'bus', 
            'Egen sykkel, el-sykkel': 'bicycle',
            'Gå': 'walk',
            'Egen bil': 'car',
            'Annet': 'car',
            'MC, moped':'motorcycle',
            'Ferge': 'ferry',
            'Bildeling': 'car sharing',
            'Tog': 'train',
            'Autocarro': 'bus',
            'Carro particular': 'car',
            'Bicicleta particular (ou e-bike)':'bicycle',
            
            
            # New mappings
            '2: Ταξί': 'taxi',
            '5: Ποδήλατο (ιδιωτικό)': 'bicycle',
            'Voiture personnelle;Marche;Transports publics;': 'train',  # Multiple mappings: car, walking, train
            'Voiture personnelle;': 'car',
            'Vélo personnel;Marche;': 'bicycle',  # Multiple mappings: bicycle, walking
            'Transports publics;Marche;': 'train',  # Multiple mappings: train, walking
            'Marche;Transports publics;Voiture partagée Mobility;': 'car sharing',  # Multiple mappings: walking, train, car sharing
            'Covoiturage;': 'ride hailing',
            'Marche;Transports publics;Vélo partagé Donkey Republic;': 'micromobility',  # Multiple mappings: walking, train, micromobility
            'Marche;Vélo personnel;Transports publics;': 'train',  # Multiple mappings: walking, bicycle, train
            'Marche;Vélo personnel;': 'bicycle',  # Multiple mappings: walking, bicycle
            'Voiture partagée Mobility;': 'car sharing',
            'Marche;Voiture personnelle;': 'car',  # Multiple mappings: walking, car
            'Marche;Transports publics;Vélo personnel;': 'train',  # Multiple mappings: walking, train, bicycle
            'Voiture personnelle;Covoiturage;': 'car',  # Multiple mappings: car, ride hailing
            'Vélo personnel;Transports publics;': 'train',  # Multiple mappings: bicycle, train
            'Vélo personnel;Voiture partagée Mobility;': 'car sharing',  # Multiple mappings: bicycle, car sharing
            'Trottrinette personnelle;': 'escooter',
            'Transports publics;Marche;Vélo personnel;': 'bicycle',  # Multiple mappings: train, walking, bicycle
            'Marche;Transports publics;Voiture personnelle;': 'car',  # Multiple mappings: walking, train, car
            'ferry': 'ferry',
            '8: Αυτοκίνητο (κοινόχρηστο)': 'car sharing',
            'Voiture personnelle;Transports publics;': 'car',  # Multiple mappings: car, train
            'Transports publics;Vélo personnel;': 'bicycle',  # Multiple mappings: train, bicycle
            'Voiture partagée Mobility;Marche;': 'car sharing',  # Multiple mappings: car sharing, walking
            'Marche;Covoiturage;': 'ride hailing',  # Multiple mappings: walking, ride hailing
            'Transports publics;Vélo personnel;Marche;': 'train',  # Multiple mappings: train, bicycle, walking
            'Transports publics;Covoiturage;': 'ride hailing',  # Multiple mappings: train, ride hailing
            'Transports publics;Vélo personnel;Vélo partagé Donkey Republic;': 'micromobility',  # Multiple mappings: train, bicycle, micromobility
            'Vélo partagé Donkey Republic;': 'micromobility',
            'Prywatny samochód': 'car',
            'Wspólny rower (lub rower elektr': 'micromobility',
            'Taksówka': 'taxi',
            'Transport pasażerski zamawiany': 'ride hailing',
            'Marche;Voiture partagée Mobility;': 'car sharing',
            'Motociclo particular': 'motorcycle',
            'A pé': 'walk',
            
            '0': 'private car',
            'Shared car': 'car sharing',
            'Private car': 'car',
            'Walking': 'walk',
            'private car': 'car',
            
            # car
            # taxi
            # train
            # bus
            # motorcycle
            # bicycle
            # escooter
            # walking
            # car sharing
            # micromobility
            # ride hailing
            
            '10: Ποδήλατο (κοινόχρηστο)': 'bicycle',
            'Private motorcycle':'motorcycle',
            'Boat': 'ferry',
            'Private bicycle (or e-bike)':'bicycle',
            'Carro partilhado':'car sharing',
            'TVDE ou transporte a pedido': 'ride hailing',
            'Bicicleta partilhada (ou e-bike)':'bicycle',
            'Metro, tram, suburban railway, etc.':'train',
            'Shared bicycle (or e-bike)': 'micromobility',
            'Private e-scooter': 'escooter',
            'Water taxi': 'water taxi',
            'Metro, tram, comboio suburbano, etc.':'train'
        
            
        }

        mapping2 = {'walking':'walk', 'carsharing': 'car sharing', 'ridehailing': 'ride hailing'}
    
    elif x == "purp":
        
        mapping2 = {999:999}
        mapping1 = {'om te winkelen': 'shopping',
                      'voor werk': 'work',
                      'voor recreatie, sport, evenement enz.': 'recreation',
                      'voor gezondheid of zorg': 'health',
                      'voor onderwijs': 'education',
                      'om terug te keren naar uw woning': 'home',
                      'voor andere activiteiten': 'other',
                      'voor bestuurszaken of persoonlijke diensten': 'services',
                      'Arbeit': 'work',
                      'Arztbesuch oder Pflege': 'health',
                      'Verwaltung oder persönliche Dienstleistungen': 'services',
                      'Ausbildung': 'education',
                      'Erholung, Sport, Veranstaltung': 'recreation',
                      'Einkaufen': 'shopping',
                      'Andere Aktivitäten': 'other',
                      '1: Εργασία': 'work',
                      '3: Αναψυχή, αθλητισμός, εκδηλώσεις': 'recreation',
                      '2: Εκπαίδευση': 'education',
                      '6: Δημόσιες ή προσωπικές υπηρεσίες': 'services',
                      '4: Αγορές': 'shopping',
                      '7: Άλλες δραστηριότητες': 'other',
                      '0: Επιστροφή στο σπίτι': 'home',
                      '5: Λόγοι υγείας ή παροχή φροντίδας': 'health',     
                     
                      # New mappings
                      'Travail': 'work',
                      'Loisirs': 'recreation',
                      'Retour au domicile': 'home',
                      'Praca': 'work',
                      'Powr?t do domu': 'home',
                      'Wzgl?dy zdrowotne lub zapewnien': 'health',
                      'Zakupy': 'shopping',
                      'Rekreacja, sport, wydarzenia, i': 'recreation',
                      'Us?ugi administracyjne lub osob': 'services',
                      'Edukacja': 'education',
                      'Inne czynno?ci': 'other',
                      
                      # Norway mappings
                      'Jobb':'work',
                      'Handletur':'shopping',
                      'Annet':'other',
                      'Fritidsaktivitet - trening, konsert, kino el.':'recreation',
                      'Besøke noen':'health',
                      'Skole/utdanning':'education',
                      'Hjemreise':'home',
                      
                      # Portugal mappings
                      "Trabalho":"work",
                      "Regresso a casa": "home",
                      "Escola": "education",
                      "Lazer, desporto, eventos, etc.": "recreation", 
                      "Assuntos pessoais": 'services',
                      "Motivos de saúde ou prestação de cuidados de saúde": "health",
                      "Compras": "shopping",
                      "Outras atividades": "other",
                      
                      
                      'Santé ou assistance': 'health',
                      'Achats': 'shopping',
                      'Autres': 'others',
                      'Etudes':'education',
                      'Administratifs': 'services',
                      'Powrót do domu': 'home',
                      'Względy zdrowotne lub zapewnien': 'health',
                      'Usługi administracyjne lub osob': 'services',
                      'Inne czynności':'other',
                      
                      'others': 'other',
                      'Work': 'work',
                      'Education': 'other', 
                      'Other activities': 'other',
                      'Return to home': 'home',
                      'Recreation, sports, events, etc.': 'recreation',
                      'Shopping': 'shopping',
                      'Administration or personal services': 'services',
                      'False':'work',
                      
                      'Health reasons or provision of care': 'health',
                      'Recreation, sports, events, etc': 'recreation',
                      'Helsegrunner':'health'
                      
                      
                      }
        
        
    
        
        
    elif x == 'gender':
        mapping2 = {999:999}
        mapping1 = {'Άνδρας': 'male', 'Männlich': 'male', 'man': 'male', 'Male': 'male', 'mezczyzna': 'male',
                'Γυναίκα': 'female', 'Weiblich': 'female', 'vrouw': 'female', 'Female': 'female', 'kobieta': 'female',
                'Divers': 'non-binary', 'non-binair': 'non-binary', 'niebinarna': 'non-binary', 'wolenie': 'non-binary',
                'Δεν απαντώ': np.nan, 'Möchte ich nicht angeben': np.nan, 'Prefer not to say': np.nan,
                'Mann': 'male',
                'Kvinne': 'female',
                'Masculino': 'male',
                'Feminino': 'female',
                'Velger å ikke svare': np.nan,
                'Prefiro não indicar': np.nan,
                'Non-binary': 'non-binary',
                'Divers': 'non-binary',  
                'Non-binär': 'non-binary',
                'Non-binary': 'non-binary'}
    
        
    elif x == 'age':
        mapping2 = {999:999}
        mapping1 = {
            '18-30 ετών': 'age_18_30', '18 bis 30 Jahre': 'age_18_30', '18-30 jaar': 'age_18_30', 
            '18 - 30 years old': 'age_18_30', '1830': 'age_18_30',
        
            '31-40 ετών': 'age_31_40', '31 bis 40 Jahre': 'age_31_40', '31-40 jaar': 'age_31_40', 
            '31 - 40 years old': 'age_31_40', '3140': 'age_31_40',
        
            '41-50 ετών': 'age_41_50', '41 bis 50 Jahre': 'age_41_50', '41-50 jaar': 'age_41_50', 
            '41 - 50 years old': 'age_41_50', '4150': 'age_41_50',
        
            '51-65 ετών': 'age_51_65', '51 bis 65 Jahre': 'age_51_65', '51-65 jaar': 'age_51_65', 
            '51 - 65 years old': 'age_51_65', '5165': 'age_51_65',
        
            'Άνω των 65 ετών': 'age_65_more', 'ouder dan 65': 'age_65_more', 'Older than 65': 'age_65_more', 
            '65plus': 'age_65_more',
            
            '31 bis 40 Jahre ': 'age_31_40',
            '51 bis 65 Jahre ': 'age_51_65', 
            '41 bis 50 Jahre ': 'age_41_50',
        
            'Δεν απαντώ': np.nan, 'Möchte ich nicht angeben': np.nan, 'Prefer not to say': np.nan, 
            'zeg ik liever niet': np.nan, 'wolenie': np.nan,
            '18 - 30 år': 'age_18_30',
            '18 - 30 anos': 'age_18_30',
            '18-30': 'age_18_30',
            '18-30 år': 'age_18_30',
            
            '31 - 40 år': 'age_31_40',
            '31 - 40 anos': 'age_31_40',
            '31-40': 'age_31_40',
            '31-40 ': 'age_31_40',
            '31 - 40 anos': 'age_31_40',
            
            '41 - 50 år': 'age_41_50',
            '41 - 50 anos': 'age_41_50',
            '41-50': 'age_41_50',
            
            '51 - 65 år': 'age_51_65',
            '51 - 65 anos': 'age_51_65',
            '51-65': 'age_51_65',
            
            'Eldre enn 65 år': 'age_65_more',
            '+ 65 anos': 'age_65_more',
            'Older then 65': 'age_65_more',
            
            'Prefiro não indicar': np.nan
            }
    elif x == "educ":
        mapping2 = {999:999}
        mapping1 = {
            'Πρωτοβάθμια εκπαίδευση (δηλ. Δημοτικό, Νηπιαγωγείο)': 'primary',
            'Volks-, Hauptschulabschluss': 'primary',
            'basisschool': 'primary',
            'Primary school': 'primary',
            'podstawowa': 'primary',
            'geen opleiding': 'primary',
        
            'Δευτεροβάθμια εκπαίδευση (δηλ. Λύκειο, Γυμνάσιο)': 'high_school',
            'Mittlere Reife, Realschul- oder gleichwertiger Abschluss': 'high_school',
            'Abitur/Hochschulreife': 'high_school',
            'Fachabitur/Fachhochschulreife': 'high_school',
            'middelbare school of voortgezet onderwijs': 'high_school',
            'Secondary or High school': 'high_school',
            'srednia': 'high_school',
        
            'Τριτοβάθμια εκπαίδευση (δηλ. Πανεπιστήμιο, ΤΕΙ)': 'bachelor',
            'Fachhochschul-/Hochschulabschluss': 'bachelor',
            'Abgeschlossene Lehre': 'bachelor',
            'bachelor': 'bachelor',
            'Bachelor': 'bachelor',
            'licencjat': 'bachelor',
        
            'Μεταπτυχιακές ή Διδακτορικές σπουδές': 'master or phd',
            'Master or PhD': 'master or phd',
            'master of gepromoveerd': 'master or phd',
            'mgrdr': 'master or phd',
            
            
            'Μεταπτυχιακές ή Διδακτορικές σπουδές ': 'master or phd',
            'Τριτοβάθμια εκπαίδευση (δηλ. Πανεπιστήμιο, ΤΕΙ) ': 'bachelor',
            'Πρωτοβάθμια εκπαίδευση (δηλ. Δημοτικό, Νηπιαγωγείο) ':'primary',
            'Fachhochschul-/Hochschulabschluss ': 'bachelor',
            'Schüler*in':'high_school',
        
            'Δεν απαντώ': np.nan,
            'Δεν απαντώ ': np.nan,
            'Χωρίς εκπαίδευση ':np.nan,
            'Möchte ich nicht angeben': np.nan,
            'zeg ik liever niet': np.nan,
            'Prefer not to say': np.nan,
            'wolenie': np.nan,
            
            'Mastergrad/PhD': 'master or phd',
            'Mestrado ou Doutoramento': 'master or phd',
            'Licenciatura': 'bachelor',
            'Grunnskole - videregående opplæring': 'high_school',
            'Ensino Secundário': 'high_school',
            'Ensino primário': 'primary',
            'No education': 'primary',
        
            'Fagskole': 'bachelor',
        
            'Velger å ikke svare': np.nan,
            'Prefiro não indicar': np.nan, 
            }
    
    elif x == "employ":
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


    else:
        mapping1 = {999:999}
        mapping2 = {999:999}
    
    return mapping1, mapping2