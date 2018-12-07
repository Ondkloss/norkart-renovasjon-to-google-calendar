import urllib.request
import configparser
import json
import logging
import tabula


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')
    return config


def get_municipality_number(municipality):
    url = 'https://register.geonorge.no/api/subregister/sosi-kodelister/kartverket/kommunenummer-alle.json'
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    j = json.load(resp)
    for item in j['containeditems']:
        if item['status'] in ['Valid', 'Gyldig'] and item['description'] == municipality:
            result = item['codevalue']
            print('Municipality number: %s' % result)
            return result

    raise ValueError('Could not determine municipality number')


def get_renovation_pdf_url(api_key, municipality_number, street_name, street_number, year):
    url = 'https://komteksky.norkart.no/komtek.renovasjonwebapi/api/tommekalenderPdf/?gatekode=0&gatenavn={}&husnr={}&aar={}'.format(urllib.parse.quote_plus(street_name), street_number, year)
    req = urllib.request.Request(url)
    req.add_header('RenovasjonAppKey', api_key)
    req.add_header('Kommunenr', municipality_number)
    resp = urllib.request.urlopen(req)
    content = resp.read().decode(resp.headers.get_content_charset())

    if content:
        content_fixed = content.replace('ø', '%C3%B8')  # URL-encode ø specifically
        print('PDF URL: %s' % content_fixed)
        return content_fixed

    raise ValueError('Could not determine PDF URL')


def create_renovation_csv(url, filename):
    df = tabula.read_pdf(url, encoding='utf-8', spreadsheet=True, pages='all')
    df.to_csv(filename, encoding='utf-8')

    with open(filename) as f:
        file_lines = f.readlines()

    file_lines = [x.strip() for x in file_lines]
    file_lines_fixed = []
    header_found = False
    prev = None

    for _index, line in enumerate(file_lines):
        # Look for header
        if line.startswith('Uke,'):
            if not header_found:
                header_found = True
            else:
                prev = None
                continue

        # Look for lines with no content
        if line.startswith(','):
            prev = None
        # Look for lines with content only
        elif not ',' in line:
            # Attach such lines to previous line, if any
            if prev is not None and file_lines_fixed:
                file_lines_fixed[-1] += line
                prev = line
        # Normal lines
        else:
            file_lines_fixed.append(line)
            prev = line

    with open(filename, "w") as f:
        f.write('\n'.join(file_lines_fixed))
