import pandas as pd

def fixCoimbra(data):
    columns_to_remove = [col for col in data.columns if col.startswith('Points') or col.startswith('Feedback')]
    data_dropped = data.drop(columns=columns_to_remove)    
    return data_dropped
