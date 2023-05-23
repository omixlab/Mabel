pubmed_filters = [["Abstract", "Free full text", "Full text"],
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

        