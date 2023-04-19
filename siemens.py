import PyPDF2
import re
import pandas as pd

print('Copyright © 2023 Shahar Rashty')
# user will input the first serie page number
first_page=int(input('First series page number:'))-1
#user will input the PDF name
file_name = input('Enter PDF name:')

# Open the PDF file
pdf_file = open(f'{file_name}.pdf', 'rb')

# Create a PDF reader object
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Get the total number of pages in the PDF file
num_pages = len(pdf_reader.pages)

# Create an empty list to store the text from each group of pages
page_groups = []

# Loop through the pages in the PDF file, grouping every 2 consecutive pages together because each series takes 2 pages at the PDF
for i in range(first_page, num_pages - 1, 2):
    # Get the text from the current page and the next page
    page_text = ''
    page = pdf_reader.pages[i]
    page2 = pdf_reader.pages[i + 1]
    page_text += page.extract_text()
    page_text += page2.extract_text()

    # Add the text from the current group of pages to the page_groups list
    page_groups.append(page_text)

# Close the PDF file
pdf_file.close()

#extract the name that appeares on every page before the series name
prefix=page_groups[0].split('\\')[-2]
# get all series names they always appears between a few back slashes and after the prefix we found
names = []
for text in page_groups:
    try:
        # names.append(re.search(r"(\\\\*{}\\\\*)(\w+.[a-zA-Z1-9\* ]+)".format(prefix), text, re.IGNORECASE).group(2))
        names.append(re.search(r"(\\\\*{}\\\\*)(.*)".format(prefix), text, re.IGNORECASE).group(2))
    except:
        continue

#creting a dictionary of dictionaries with series names as outer dict keys
my_dict = {}
for name in names:
    my_dict[name] = {}
# print(my_dict)

# extracting the parameters using Regex
for page_group, key in zip(page_groups, my_dict):
    try:
        my_dict[key]['Pulse sequence'] = re.search(r'(SNR: 1.00 :\s+(\w+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Pulse sequence'] = ('')

    try:
        my_dict[key]['TA'] = re.search(r'(TA:\s+(\d+:\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['TA'] = ('')

    try:
        my_dict[key]['slices'] = re.search(r'(Slices\s+(\d+(\.)?\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['slices'] = ('')

    try:
        my_dict[key]['tr'] = re.search(r'(TR\s+(\d+(\.)?\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['tr'] = ('')

    try:
        my_dict[key]['te'] = re.search(r'(TE\s+(\d+(\.)?\d+|\d+(\.)?\d+ \w+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['te'] = ('')
    try:
        my_dict[key]['ti'] = re.search(r'(TI\s+(\d+(\.)?\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['ti'] = ('')

    try:
        my_dict[key]['thickness'] = re.search(r'(Slice thickness\s+(\d+(\.)?\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['thickness'] = ('')

    try:
        my_dict[key]['Base'] = re.search(r'(Base resolution\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Base'] = ('')

    try:
        my_dict[key]['phase'] = re.search(r'(Phase resolution\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['phase'] = ('')

    try:
        my_dict[key]['Concatenations'] = re.search(r'(Concatenations\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Concatenations'] = ('')

    try:
        my_dict[key]['Averages'] = re.search(r'(Averages\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Averages'] = ('')

    try:
        my_dict[key]['Fourier'] = re.search(r'(Phase partial Fourier\s+(\w+.?[1-9]*))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Fourier'] = ('')

    try:
        my_dict[key]['GRAPPA number'] = re.search(r'(Acceleration Factor PE\s+([1-9]*))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['GRAPPA number'] = ('')

    try:
        my_dict[key]['Acceleration mode'] = re.search(r'(Acceleration mode\s+(\w*))', page_group,
                                                  re.IGNORECASE).group(2)
    except:
        my_dict[key]['Acceleration mode'] = ('')

    try:
        my_dict[key]['PAT'] = re.search(r'(PAT mode\s+(\w+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['PAT'] = ('')

    try:
        my_dict[key]['GRAPPA number PAT'] = re.search(r'(Accel. factor PE\s+([1-9]*))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['GRAPPA number PAT'] = ('')

    try:
        my_dict[key]['Dist'] = re.search(r'(Dist. factor\s+(\d+(\.)?\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Dist'] = ('')

    try:
        my_dict[key]['Bandwidth'] = re.search(r'(Bandwidth\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Bandwidth'] = ('')

    try:
        my_dict[key]['Turbo'] = re.search(r'(Turbo factor\s+(\d+))', page_group, re.IGNORECASE).group(2)
    except:
        my_dict[key]['Turbo'] = ('')


# Creating DF from dict
df = pd.DataFrame.from_dict(my_dict, orient='index')

# concatenate to create new columns as needed
df['Avg/Con'] = df['Averages'].astype(str) + '/' + df['Concatenations'].astype(str)
df["Resolution [Freq/Phase]"] = df['Base'].astype(str) + '/' + df['phase'].astype(str) + '%'

df['#slices/thick/gap%'] = df['slices'].astype(str) + '/' + df['thickness'].astype(str) + '/' + df['Dist'].astype(str)
df['TR/TE/TI'] = df['tr'].astype(str) + '/' + df['te'].astype(str) + '/' + df['ti'].astype(str)

df['Parallel Imaging'] = df['Acceleration mode'].astype(str) + df['GRAPPA number'].astype(str)
df['PAT MODE'] = df['PAT'].astype(str) + df['GRAPPA number PAT'].astype(str)

df.drop(['slices', 'thickness', 'Dist','tr','te','Averages','Concatenations','Base','phase','Acceleration mode','PAT'], axis=1, inplace=True)
df["Parallel Imaging"] = df["Parallel Imaging"].str.replace("Resolution", "")
df["PAT MODE"] = df["PAT MODE"].str.replace("Resolution", "")

# write the dataframe to an excel file
df.to_excel(f'{file_name}.xlsx', index_label='Key')
print(df)