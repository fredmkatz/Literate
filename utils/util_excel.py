import pandas as pd
from typing import List, Dict




def read_excel_sheet(excel_file_path, sheet_name) -> List[Dict]:
    # Read the Excel file into a pandas DataFrame
    # By default, read_excel reads the first sheet. 
    # Use the 'sheet_name' argument to specify a different sheet.
    df = pd.read_excel(excel_file_path, sheet_name)
    
    # Convert the DataFrame to a list of dictionaries, where each dictionary
    # represents a row and column headers become dictionary keys.
    dicts = df.to_dict(orient='records')
    return dicts

def read_annotation_types():
    configs_path = r"ldm\ldm_models\ldm_assets\Literate_config.xlsx"

    the_dicts = read_excel_sheet(configs_path, "AnnotationTypes")
    annotation_types = {}
    for the_dict in the_dicts:
        atype = the_dict["TypeName"]
        emoji = the_dict['Emoji']
        purpose = the_dict["Purpose"]
        
        annotation_types[atype.lower()] = the_dict
    return annotation_types
    

if __name__ == "__main__":
    configs_path = r"ldm\ldm_models\ldm_assets\Literate_config.xlsx"

    the_dicts = read_excel_sheet(configs_path, "AnnotationTypes")
    print(the_dicts)
    
    atypes = read_annotation_types()
    
    print("Annotation types: ", atypes)