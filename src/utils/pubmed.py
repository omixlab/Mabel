# PUBMED
tags = (
        'All Fields', 'Date', 'Author', 'Affiliation', 'Book', 'Journal', 'Volume', 
        'Pagination', 'Title', 'Title/Abstract', 'Transliterated Title', 'Text Word',
        'Language', 'MeSH', 'Pharmacological Action', 'Conflict of Interest Statements', 
        'EC/RN Number', 'Grant Number', 'ISBN', 'Investigator', 'Issue', 'Location ID',
        'Secondary Source ID', 'Other Term', 'Publication Type', 'Publisher', 
        'Subject - Personal Name', 'Supplementary Concept',  
        )

radios = {
        'Author': ('Author', 'Author - Corporate', 'Author - First', 'Author - Last', 'Author - Identifier'),
        'MeSH': ('MeSH Major Topic', 'MeSH Subheading', 'MeSH Terms'),
        'Date': ('Date - Completion', 'Date - Create', 'Date - Entry', 'Date - MeSH', 'Date Modification', 'Date Publication')
        }

filters = [
        ["Abstract", "Free full text", "Full text"],
        ["Books and documents", "Clinical trial", "Meta-Analysis", "Randomized Controlled Trial", "Review", "Systematic Review"],
        ["Humans", "Other Animals", "Male", "Female"],
        ["English", "Portuguese", "Spanish"],
        ["Associated data", "Exclude preprints", "MEDLINE"]
        ]
    

dict = {
        "Abstract": 'fha', 
        "Free full text": 'ffrft', 
        "Full text": 'fft',
        "Books and documents": 'pubt.booksdocs', 
        "Clinical trial": 'pubt.clinicaltrial',
        "Meta-Analysis": 'pubt.meta-analysis',
        "Randomized Controlled Trial": 'pubt.randomizedcontrolledtrial',
        "Review": 'pubt.review',
        "Systematic Review": 'pubt.systematicreview',

        "Humans": 'hum_ani.humans',
        "Other Animals": 'hum_ani.animal',
        "Male": 'sex.male',
        "Female": 'sex.female',

        "English": 'lang.english',
        "Portuguese": 'lang.portuguese',
        "Spanish": 'lang.spanish',

        "Associated data": 'articleattr.data', 
        "Exclude preprints": 'other.excludepreprints',
        "MEDLINE": 'other.medline'
        }


