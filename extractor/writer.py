from pathlib import Path
from typing import Dict, List
import pandas as pd

"""Writer module for exporting extracted contact data to Excel."""




def write_excel(records: List[Dict], out_path: Path) -> None:
    """
    Write contact records to an Excel file with contacts and summary sheets.
    
    Args:
        records: List of dictionaries containing contact information.
                 Expected keys: 'name', 'email', 'phone', 'source_url'
        out_path: Path object specifying where to write the Excel file.
    
    The function creates two sheets:
        - 'contacts': All valid contact records
        - 'summary': Metrics including total rows, unique emails, and unique phones
    """
    # Build DataFrame with specified columns
    df = pd.DataFrame(records, columns=['name', 'email', 'phone', 'source_url'])
    
    # Fill NaN values with empty strings for consistent filtering
    df = df.fillna('')
    
    # Drop rows where name, email, and phone are all empty
    df = df[~((df['name'] == '') & (df['email'] == '') & (df['phone'] == ''))]
    
    # Sort by name, email, phone for readability
    df = df.sort_values(by=['name', 'email', 'phone'], ignore_index=True)
    
    # Calculate summary metrics
    total_rows = len(df)
    unique_emails = df[df['email'] != '']['email'].nunique()
    unique_phones = df[df['phone'] != '']['phone'].nunique()
    
    summary_data = {
        'Metric': ['total_rows', 'unique_emails', 'unique_phones'],
        'Value': [total_rows, unique_emails, unique_phones]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Write to Excel with two sheets using openpyxl engine
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='contacts', index=False)
        summary_df.to_excel(writer, sheet_name='summary', index=False)