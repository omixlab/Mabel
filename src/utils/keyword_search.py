# Temporary file running locally instead of importing this lib

import pandas as pd
import re
import string
import copy

TERM_EXPRESSION = '([a-zA-Z0-9.@_]+:[a-zA-Z0-9_\- ]+)'

def trim_strings(raw_string):
    trim_string = copy.copy(raw_string)
    for char in string.whitespace + "'\"":
        trim_string = trim_string.strip(char)
    trim_string = re.sub('\W+', ' ', trim_string)
    return trim_string

def keyword_search(df, raw_query, return_query_expression=False, case_sensitive=False):
    '''
    Process a query string with field indicator for Pandas Dataframe
    collumns. Currently, only "str.contains" queries are performed.
    Boolean operations (and, or, not) are mantained during compilation.

    Searched field should not contain spaces or ":".

    Examples:

    ((title:leptospira) and (abstract:vaccine))
    '''
    terms = re.findall(TERM_EXPRESSION, raw_query)
    compiled_query = raw_query
    
    for term in terms:
        field, keyword = term.split(':', 1)
        field   = trim_strings(field)
        keyword = trim_strings(keyword)
        
        if field not in df.columns:
            raise Exception(f'field "{field}" is not present in dataframe')
        
        if field == 'date':
            start_date = int(keyword.split(" ")[0])
            end_date = int(keyword.split(" ")[1])
            df['date'] = df['date'].str.slice(0, 4).astype(int)
            compiled_term = f'date >= {start_date} and date <= {end_date}'
            
        else:
            compiled_term = f'{field}.str.contains("{keyword}", na=False, case={case_sensitive})'

        compiled_query = compiled_query.replace(
            term, 
            compiled_term
        )
    try:
        if return_query_expression:
            return df.query(compiled_query), compiled_query
        else:
            return df.query(compiled_query)
    except:
        raise Exception('invalid query')
