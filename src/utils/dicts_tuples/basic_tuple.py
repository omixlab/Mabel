tags = [
    (1, "All Fields"),
    (2, "Title"),
    (3, "Abstract"),
    (4, "Author"),
    (5, "Affiliation"),
    (6, "Pages"),
    (7, "Volume"),
    (8, "Language"),
    (9, "Publication Type"),
    (10, "Publisher"),
]

to_pubmed = {
    "All Fields": "",
    "Date": "[Date Publication]",
    "Title": "[Title]",
    "Abstract": "[Title/Abstract]",
    "Author": "[Author]",
    "Affiliation": "[Affiliation]",
    "Pages": "[Pagination]",
    "Volume": "[Volume]",
    "Language": "[Language]",
    "Publication Type": "[Publication Type]",
    "Publisher": "[Publisher]",
}

to_scopus = {
    "All Fields": "ALL",
    "Date": "PUBYEAR",
    "Title": "TITLE",
    "Abstract": "ABS",
    "Author": "AUTH",
    "Affiliation": "AFFIL",
    "Pages": "PAGES",
    "Volume": "VOLUME",
    "Language": "LANGUAGE",
    "Publication Type": "DOCTYPE",
    "Publisher": "PUBLISHER",
}

document_type = {
    "Article": "ar",
    "Abstract report": "ab",
    "Book": "bk",
    "Business article": "bz",
    "Book chapter": "ch",
    "Conference paper": "cp",
    "Conference review": "cr",
    "Editorial": "ed",
    "Erratum": "er",
    "Letter": "le",
    "Note": "no",
    "Press release": "pr",
    "Review": "re",
    "Short survey": "sh",
}
