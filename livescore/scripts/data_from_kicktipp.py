import requests, zipfile, io, csv

with requests.session() as s:
    p1 = s.get('https://www.kicktipp.com/info/profil/login')
    auth_data = {'kennung': 'ivan.jakovac2@gmail.com', 'passwort': 'Ijakovac999'}
    p2 = s.post('https://www.kicktipp.com/info/profil/loginaction', data=auth_data)
    download_data = {'tippsaisonId': 1084573, 'datenauswahl': 'tipps', 'tippspieltagIndex': 2, 'wertung': 'einzelwertung'}
    p3 = s.post('https://www.kicktipp.com/trutinebezobrazne/spielleiter/datenexport', data=download_data, stream=True)
    zip_file = zipfile.ZipFile(io.BytesIO(p3.content))
    with zip_file.open(zip_file.namelist()[0], 'r') as bytesCSV:
        filedata = list(csv.reader(io.TextIOWrapper(bytesCSV, 'utf-8'),delimiter=';'))
        header = filedata[0]
        for row in filedata[1:]:
            id = row[1]
            for i, prediction in enumerate(row[2:]):
                print({'id': id, 'game': header[i+2], 'prediction': prediction})