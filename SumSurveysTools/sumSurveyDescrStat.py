import pandas as pd
import os

root_dir = os.path.dirname(os.path.realpath(__file__))

from googletrans import Translator
def transEnglish(text, src_lang = "auto"):
    translator = Translator()
    translated_text = translator.translate(text, src=src_lang, dest='en')
    return translated_text.text

xls = pd.ExcelFile('SUMsocioDemo.xlsx')
dfs = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}

def SocioDemoDescr(city, xls):

    df = xls.parse(city)

 
    for column in df.columns:
        column_data = df[column]
        frequency = column_data.value_counts(normalize = True) * 100
            
        print(f"Column: {column}")
        for value, percent in frequency.items():
            transvalue = transEnglish(value, 'auto')
            print(f"\t{transvalue}: {percent:.2f}%")
        print()
    print()

print(SocioDemoDescr ('Coimbra', xls))


#
df = xls.parse("Krakow")
frequency = df["age"].value_counts()
print(frequency)

