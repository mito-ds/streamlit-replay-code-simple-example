from mitosheet.public.v3 import *
import pandas as pd

def function_automation_script():
    # Imported performance.csv
    performance = pd.read_csv(r'/Users/aarondiamond-reivich/Desktop/streamlit-simple-replay/data/performance.csv')
    
    return performance

performance = function_automation_script()