# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 13:28:17 2020

@author: Asja
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:07:45 2020

@author: Asja
"""

import os
import csv
import pandas as pd
from statistics import mean, stdev, median
import re
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice


NUM = '[0-9]'
YEAR = r'(?P<year>(2[ ]?0[  ]?[0|1|2][ ]?[0-9])|(1[ ]?9[ ]?[0-9][ ]?[0-9]))'
# YEAR = r'(?P<year>(20[0|1|2][0-9])|(19[9|8|7|6][0-9]))'
# TO DOOOOOOOOO
LIST_TYPES = list(pd.read_excel('D:/python/remote_config/ml_training/KG/docs/types_cleaned.xlsx', index=False)['types'])
NEGATIVE_EXAMPLE = ['//', 'html', '?', '.pdf']

# Split pdf to paragraph
def from_pdf_to_list_paragraphs(path):
    document = open(path, 'rb')
    #Create resource manager
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    paragraphs = []
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(document):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
#        print (layout)
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                paragraphs.append(element.get_text())
    return paragraphs

# Save paragraphs to csv_file and excel
def from_list_paragraphs_to_excel(paragraphs, path):
    first = pd.DataFrame()
    first['paragraphs'] = paragraphs
    first.to_excel(path, index = False)
    
def from_list_paragraphs_to_csv(paragraphs, path):
    first = pd.DataFrame()
    first['paragraphs'] = paragraphs
    first.to_csv(path, index = False)

# Cut all strings above "Publicationen"    
def cut_publication_list(paragraphs):
#    print (len(paragraphs))
    i = 0
    for item in paragraphs:
        if paragraphs[i].lower().count('publi') != 0:
            if len(paragraphs[i]) < 65:
                break
            else:
                i+=1
        elif paragraphs[i].lower().count('ffentlichung') != 0:
            if len(paragraphs[i]) < 65:
                break
            else:
                i+=1
        else:
            i+=1
    if len(paragraphs[i:]) < 6:
        result = paragraphs
    else:
        result = paragraphs[i:]        
#    print (len(result))
    return result        

# Get list of files on directory
def get_pdf_list(path):
    files = os.listdir(path)
    pdfs = filter(lambda x: x.endswith('.pdf'), files)
    return pdfs
    
# Moda of length of strings
def stats_len_str(list_strings):
    means = mean([len(i) for i in list_strings])
    std = stdev ([len(i) for i in list_strings])
    return means, std

# recombination of one paragraph
def split_to_bibl_items(paragraph):
    npar = []
    new_paragraph = ''
    old = paragraph.split('\n')
    i = 0
    mean, std = stats_len_str(old)    
    while i < len(old):
        if i == (len(old)-2):
#            print (new_paragraph)
            new_paragraph+= old[i] + '\n'+ old[i+1] + '\n'
            npar.append(new_paragraph)
            i+=1
            break
        if re.search(YEAR, old[i]) is None:
            new_paragraph = new_paragraph + old[i] + '\n'
            i += 1
            if i == len(old):
                npar.append(new_paragraph)
                
        else:                
            if (len(old[i]) - len(old[i+1])) > 5  :
                new_paragraph = new_paragraph + old[i] + '\n' + old[i+1] + '\n'
                i +=2
                npar.append(new_paragraph)
                new_paragraph = ''
            else:
                if (len(old[i+1]) - len(old[i+2])) > 5:
                    new_paragraph = new_paragraph + old[i] + '\n'+ old[i+1] + '\n'+ old[i+2] + '\n'
                    npar.append(new_paragraph)
                    new_paragraph = ''
                    i+=3
                else:    
                    new_paragraph = new_paragraph + old[i] + '\n'                     
                    npar.append(new_paragraph)
                    new_paragraph = ''
                    i +=1
                
    return npar 
 


# go through all paragraphs    
def recombine_paragraphs(paragraphs):    
    new_paragraphs = []
    for item in paragraphs:
        if type(item) == str:
            if len(item.split('\n')) > 5:
                for paragr in split_to_bibl_items(item):
                    new_paragraphs.append(paragr)       
            else:
                new_paragraphs.append(item)
        else:
                new_paragraphs.append(item)
#    new_paragraphs = fix_mistakes_recombination(new_paragraphs)
    return new_paragraphs    

def fix_mistakes_recombination(paragraphs):
    new_combination = []
    i = 0
    while i < len(paragraphs):
        
        banch = paragraphs[i]
        if i == (len(paragraphs)-1):
            new_combination.append(banch)
            i+=1
            break
            
        if len(paragraphs[i+1].split('/n'))==1:
            # if paragraphs[i+1].count('://') > 0:
            #     banch = banch + paragraphs[i+1]
            #     new_combination.append(banch)
            #     i+=2
            if (')' in paragraphs[i+1]) and ('(' in paragraphs[i+1]):
                banch = banch + paragraphs[i+1]
                new_combination.append(banch)
                i+=2
        
            elif (']' in paragraphs[i+1]) and ('[' in paragraphs[i+1]):
                banch = banch + paragraphs[i+1]
                new_combination.append(banch)
                i+=2
                
            elif (paragraphs[i+1].find('In:') >-1) and (paragraphs[i+1].find('In:') < 5):
                banch = banch + paragraphs[i+1]
                new_combination.append(banch)
                i+=2
                
            elif (paragraphs[i+1].find('in:') >-1) and (paragraphs[i+1].find('in:') < 5):
                banch = banch + paragraphs[i+1]
                new_combination.append(banch)
                i+=2
                
            else:
                new_combination.append(banch)
                i+=1
        else:
            new_combination.append(banch)
            i+=1                
                    
    return new_combination

# Посчитать максимальную длину параграфа
def median_lenght(paragraphs):
    l = 0
    for par in paragraphs:
        if len(par.split('\n')) > 20:
            l+=3
        elif len(par.split('\n')) > 15:
            l+=2
        elif len(par.split('\n')) > 6:
            l+=1
            

    return l
            
def parse_years_raw(paragraphs):
    year_line = []
    for item in paragraphs:
        years = list(re.finditer(YEAR, item))
        if len(years) > 0:
            year_line.append(', '.join([i.group('year') for i in years]))
        else:
            year_line.append(None)
    return year_line

def get_csv_list(path):
    files = os.listdir(path)
    csvs = filter(lambda x: x.endswith('.csv'), files)
    return csvs

def get_excel_list(path):
    files = os.listdir(path)
    xlsx = filter(lambda x: x.endswith('.xlsx'), files)
    return xlsx

# Parse all years from record
def parse_years_raw(paragraphs):
    year_line = []
    for item in paragraphs:
        years = list(re.finditer(YEAR, str(item)))
        if len(years) > 0:
            year_line.append(','.join([i.group('year').replace(' ', '') for i in years]))
        else:
            year_line.append(None)
    return year_line 


def all_type_of_publ(paragraphs):
    list_of_types = []
    for par in paragraphs:
        if type(par) == str:
            typ = par.split('\n')[0] 
            if len(typ.split(' ')) < 5:
                if not re.findall(NUM, typ): 
                    list_of_types.append(typ)
    return list_of_types 



# Цикл для экстракции списка типа публикации
# TODODODODODOD Вдруг тип не в первой строке, а во втрой??????
def extract_type_publ(paragraphs):
    list_par_types = []
    typepub = None
    for par in paragraphs:
        typ = str(par).split('\n')[0].strip().replace('\xa0', ' ').lower()
        if typ == '':
            typ = par.split('\n')[1].strip().replace('\xa0', ' ').lower()
        i = 0
        for word in LIST_TYPES:
            if typ.count(word.lower())> 0:
                i+=1
                
        if len(typ.split(' ')) < 6:
            if i > 0:
                k = 0
                for neg in NEGATIVE_EXAMPLE:
                    if typ.lower().count(neg.lower())> 0:
                        k+=1
                if k == 0:    
                    typepub = typ
                    print('++++')
                    print(typ.split(' '))
                    print(typepub)
                    print('----------')
        list_par_types.append(typepub)
    
    return list_par_types


def get_time_filt_index(l_years, window):
    bunch = [0]*window
    cent = window//2
    final_list = []
    
    for i in range(0, len(l_years)+1):
        bunch = bunch[1:]
        bunch.append(i)       
        if l_years[bunch[cent]]:
            years = [int(x) for x in(l_years[bunch[cent]].split(','))]
            if len(years) > 0:
                final_list += bunch
    final_list = list(set(final_list))
    result = filter(lambda x: x < len(l_years), final_list)     
    return result


def check_empty_from_pdf(path):

    files = list(get_pdf_list(path))
#    len(files)
    empty = []
#    for pdf in files:
#        print(pdf.split('.pdf')[0])    
    for item in files:
        paragraphs = from_pdf_to_list_paragraphs(path+'/'+item)
#        paragraphs = cut_publication_list(paragraphs)
#        paragraphs = recombine_paragraphs(paragraphs)
        print(item)
        name = item.split('.pdf')[0]
        if len(paragraphs) == 0:
            empty.append(name)
                        
    empty = pd.DataFrame(empty, columns = ['empty'])
    empty.to_excel('empty_from_pdf.xlsx', index= False)
    return empty

def extract_and_split(path):
    files = list(get_pdf_list(path))
    len(files)
    # for pdf in files:
    #     print(pdf.split('.pdf')[0])    
    for item in files:
        paragraphs = from_pdf_to_list_paragraphs(path+'/'+item)
        paragr = []
        for par in paragraphs:
            par = par.replace('2 0 0 9', '2009')
            par = par.replace('2 0 1 0', '2010')
            par = par.replace('2 0 1 1', '2011')
            par = par.replace('2 0 1 2', '2012')
            par = par.replace('2 0 1 3', '2013')
            par = par.replace('2 0 1 4', '2014')
            par = par.replace('2 0 1 5', '2015')
            par = par.replace('2 0 1 6', '2016')
            par = par.replace('2 0 1 7', '2017')
            par = par.replace('2 0 0 8', '2008')
            par = par.replace('2 0 0 7', '2007')
            par = par.replace('2 0 0 6', '2006')
            par = par.replace('2 0 0 5', '2005')
            par = par.replace('2 0 0 4', '2004')
            par = par.replace('2 0 0 3', '2003')
            par = par.replace('2 0 0 2', '2002')
            par = par.replace('2 0 0 1', '2001')
            par = par.replace('2 0 0 0', '2000')
            paragr.append(par)
#        paragraphs = cut_publication_list(paragraphs)
        paragraphs = recombine_paragraphs(paragr)
        paragraphs = fix_mistakes_recombination(paragraphs)
        name = item.split('.pdf')[0]
    # save files in separate dir "csv"
        print(item)                
        from_list_paragraphs_to_excel(paragraphs, 'xlsx/'+str(name)+'.xlsx')
#        from_list_paragraphs_to_csv(paragraphs, 'csv/'+str(name)+'.csv')


def extention_list_of_types(path, types_path):
    sg_files = list(get_csv_list(path+'/csv'))
    types = pd.read_csv(types_path+'/types_cleaned.csv')
    LIST_TYPES = list(types['types'])
    NEGATIVE_EXAMPLE = ['//', 'html', '?', '.pdf']    

    list_types = []
    for item in sg_files:
        pd_paragraphs = pd.read_csv(path+'/csv/'+item)
        paragraphs = list(pd_paragraphs['paragraphs'])
        list_types+= all_type_of_publ(paragraphs)
    
    # Filter list of type_publ
        
    filtered_list = []    
    for typ in list_types:
        i =0
        for word in LIST_TYPES:
            if typ.lower().count(word.lower())> 0:
                i+=1
        if i == 0:        
            filtered_list.append(typ)
                
    filtered_list = list(set(filtered_list))    
    sp = pd.DataFrame()
    sp['types'] = filtered_list
    sp.to_excel(types_path+'/extention_types.xlsx')         

def recombination_of_paragraphs(xlsx):
    files = list(get_excel_list(xlsx))  
    for item in files:
        parar = pd.read_excel('xlsx/'+item)
        paragraphs =list(parar['paragraphs'])
        paragraphs = recombine_paragraphs(paragraphs)
    # save files in separate dir "xlsx_r"
        print(item)
        name = item.split('.xlsx')[0]                
        from_list_paragraphs_to_excel(paragraphs, 'xlsx_r/'+str(name)+'.xlsx')

def filtration(xlsx_r, x):
    files = list(get_excel_list(xlsx_r+'/xlsx')) 
    for item in files:
        print(item)
        pd_paragraphs = pd.read_excel('xlsx/'+item)
        paragraphs = list(pd_paragraphs['paragraphs'])
        pd_paragraphs['years_extr'] = parse_years_raw(paragraphs)
        pd_paragraphs['type_publ_extr'] = extract_type_publ(paragraphs)
    #    pd_paragraphs.to_csv('csv_years/'+str(item.split('.csv')[0])+'_years.csv', index = False)            
        filtered_par = pd_paragraphs.loc[get_time_filt_index(pd_paragraphs['years_extr'], x)]
        name = item.split('.xlsx')[0]
        filtered_par.to_excel('excel_filtered/'+str(name)+'_filtered.xlsx', index = False)

