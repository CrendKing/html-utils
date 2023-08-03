'''
Given an URL to a Wikipedia page with comparison tables, merge all the tables using the primary key, then output as CSV.
'''

from urllib.request import urlopen
import argparse
import bs4
import pandas
import sys


def get_cell_effective_text(cell):
    if cell.img:
        return ' '.join((img.get('alt') for img in cell.find_all('img')))
    else:
        return cell.get_text().strip()

argParser = argparse.ArgumentParser()
argParser.add_argument('url')
argParser.add_argument('--out-file')
args = argParser.parse_args()

html_source = urlopen(args.url).read().decode()
html_soup = bs4.BeautifulSoup(html_source, 'html.parser')
combined_dataframe = None

for wikitable in html_soup.find_all('table', class_='wikitable'):
    headers = []
    data = []

    for ref in wikitable.find_all(class_='reference'):
        ref.extract()

    header_rows = wikitable.td.find_parent('tr').find_previous_siblings('tr')
    data_rows = header_rows[-1].find_next_siblings('tr')

    if len(header_rows) > 1:
        # if the table have multiple rows as header, we assume the last row covers all column names for the first row

        last_row_cells = header_rows[0].find_all('th')
        last_row_index = 0

        for cell in header_rows[-1].find_all('th'):
            colspan = int(cell.get('colspan', '0'))
            if colspan:
                for i in range(colspan):
                    headers.append(get_cell_effective_text(last_row_cells[last_row_index]))
                    last_row_index += 1
            else:
                headers.append(get_cell_effective_text(cell))

    else:
        headers = [get_cell_effective_text(cell) for cell in header_rows[0].find_all('th')]

    for tr in data_rows:
        '''
        in a wikitable, the first column of each row is always <th>
        if the other columns are also <th>, it is a header row, and we only need the first one if there are multiple
        otherwise, it is a data row, and we use the value of the first column as the primary key for merging
        '''

        if tr.td:
            data.append([get_cell_effective_text(cell) for cell in tr.find_all(('th', 'td'))][0:len(headers)])

    curr_dataframe = pandas.DataFrame(data, columns=headers, copy=False).set_index(headers[0])
    combined_dataframe = curr_dataframe if combined_dataframe is None else combined_dataframe.combine_first(curr_dataframe)

if combined_dataframe is None:
    print("No Wikitable in URL")
else:
    with open(args.out_file, 'w', newline='') if args.out_file else sys.stdout as output:
        combined_dataframe.to_csv(output, na_rep='?')
