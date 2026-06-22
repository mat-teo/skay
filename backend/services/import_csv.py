import io
import csv
import pandas as pd
from typing import Optional

def clean_and_parse_bank_csv(content_str: str) -> pd.DataFrame:
    """
    Safely strips metadata headers and handles inner-line newlines.
    """
    f = io.StringIO(content_str)
    
    # Simple separator pre-check
    first_lines = content_str.split('\n')[:15]
    sep = ';' if any(';' in line for line in first_lines) else ','
    
    # csv.reader naturally respects quoted fields containing newlines
    reader = csv.reader(io.StringIO(content_str), delimiter=sep)
    all_rows = list(reader)
    
    header_idx = -1
    for idx, row in enumerate(all_rows):
        row_str = " ".join(row).lower()
        if ('date' in row_str or 'data' in row_str) and \
           ('amount' in row_str or 'importo' in row_str or 'balance' in row_str):
            header_idx = idx
            break
            
    if header_idx == -1:
        header_idx = 0
        
    clean_rows = all_rows[header_idx:]
    if not clean_rows:
        return pd.DataFrame()
        
    headers = [h.strip().replace('"', '').lower() for h in clean_rows[0]]
    data_rows = clean_rows[1:]
    
    # Exclude system summary metadata or dividers
    data_rows = [r for r in data_rows if r and not (r[0].startswith('Total') or r[0].startswith('---'))]
    
    df = pd.DataFrame(data_rows, columns=headers)
    return df

def parse_amount(val) -> Optional[float]:
    if val is None or pd.isna(val):
        return None
    
    val_str = str(val).strip().replace('"', '')
    for symbol in ['€', '$', '£', 'EUR', 'USD']:
        val_str = val_str.replace(symbol, '')
        
    val_str = val_str.strip()
    if not val_str:
        return None

    if ',' in val_str and '.' in val_str:
        if val_str.find('.') < val_str.find(','):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')

    try:
        return float(val_str)
    except ValueError:
        return None