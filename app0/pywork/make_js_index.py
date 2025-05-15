# coding=utf-8
""" make_js_index.py for MĀLAVIKĀGNIMITRA
"""
from __future__ import print_function
import sys, re, codecs
import json

def int_to_roman(n):
    val_map = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    
    roman_numeral = ''
    for value, numeral in val_map:
        while n >= value:
            roman_numeral += numeral
            n -= value
            
    return roman_numeral

# Example usage:
#num = int(input("Enter a positive integer: "))
#print(f"Roman numeral: {int_to_roman(num)}")

def roman_to_int(roman):
 droman_int = {'I':1, 'II':2, 'III':3, 'IV':4,
                'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9,
                'X':10, 'XI':11, 'XII':12,'':0}
 if roman in droman_int:
  return droman_int[roman]
 else:
  # error condition
  return None
 
# global parameters
parm_regex_split = '\t' #    r'[ ]+'
parm_numcols = 5
parm_numparm = 2  
#parm_vol = r'^(I|II)$'
parm_page = r'^([0-9]+)$'
parm_anka = r'^([0-9]+)$'
parm_fromv = r'^([0-9]+)([ab])?$'
parm_tov = r'^([0-9]+)([ab])?$'
parm_ipage = r'^([0-9]+)$'   # not used
parm_vpstr_format = '%03d'  # MĀLAVIKĀGNIMITRA only needs 2 (< 100 pages for verses)

class Pagerec(object):
 """
Format of malavikagni
page, anka, fromv, tov ipage

Note the first line (column names) is ignored
""" 
 def __init__(self,line,iline,filevol=None):
  line = line.rstrip('\r\n')
  self.line = line
  self.iline = iline
  parts = re.split(parm_regex_split,line)
  self.status = True  # assume all is well
  self.status_message = 'All is ok'
  if len(parts) != parm_numcols:
   self.status = False
   self.message = 'Expected %s values. Found %s value' %(parm_numcols,len(parts))
   return
  # give names to the column values
  #raw_vol = parts[0]
  raw_page = parts[0] # internal to volume. digits
  raw_anka = parts[1]
  raw_fromv = parts[2]
  raw_tov = parts[3]
  raw_ipage = parts[4]
  # check vol
  #_vol = re.search(parm_vol,raw_vol)
  #f m_vol == None:
  #self.status = False
  #self.status_message = 'Unexpected vol: %s' % raw_vol
  #return
  # check page 
  m_page = re.search(parm_page,raw_page)
  if m_page == None:
   self.status = False
   self.status_message = 'Unexpected page: %s' % raw_page
   return
  # check anka
  m_anka = re.search(parm_anka,raw_anka)
  if m_anka == None:
   self.status = False
   self.status_message = 'Unexpected anka: %s' % raw_anka
   return
  # check fromv 
  m_fromv = re.search(parm_fromv,raw_fromv)
  if m_fromv == None:
   self.status = False
   self.status_message = 'Unexpected fromv: %s' % raw_fromv
   return
  # check tov 
  m_tov = re.search(parm_tov,raw_tov)
  if m_tov == None:
   self.status = False
   self.status_message = 'Unexpected tov: %s' % raw_tov
   return
  # check ipage
  m_ipage = re.search(parm_ipage,raw_ipage)
  if m_ipage == None:
   self.status = False
   self.status_message = 'Unexpected ipage: %s' % rawi_page
   return

  # set self.vol as integer
  #self.vol = roman_to_int(raw_vol)
  # set self.page as integer
  self.page = int(m_page.group(1))
  # set self.anka as integer
  self.anka = int(m_anka.group(1))
  # set self.fromv as integer
  self.fromv = int(m_fromv.group(1))
  x1 =  m_fromv.group(2)
  if x1 == None:
   self.fromvx = ''
  else:
   self.fromvx = x1;
  # set self.tov as integer
  self.tov = int(m_tov.group(1))
  x2 =  m_tov.group(2)
  if x2 == None:
   self.tovx = ''
  else:
   self.tovx = x2;
  # set self.ipage as integer
  self.ipage = int(m_ipage.group(1))
  # vpstr  # format consistent with format of filename of scanned page
  self.vpstr = parm_vpstr_format % self.page
  ######
  # title of each page
  self.title = 'Page %s (%s,%s-%s)' %(self.ipage,self.anka,self.fromv,self.tov)
  
 def todict(self):
  e = {
   'page':int(self.page),
   'title':self.title,
   'ipage':str(self.ipage),
   'vp':self.vpstr
  }
  return e

def init_pagerecs_main(filein,filevol=None):
 """ filein is a csv file, with first line as fieldnames
 """
 recs = []
 with codecs.open(filein,"r","utf-8") as f:
  for iline,line in enumerate(f):
   if (iline == 0):
    # assert line.startswith('volume') # skip column-title line
    print('Skipping column title line:',line)
    continue
   pagerec = Pagerec(line,iline,filevol=None)
   if pagerec.status:
    # No problems noted
    recs.append(pagerec)
   else:
    lnum = iline + 1
    print('Problem at line # %s:' % lnum)
    print('line=',line)
    print('message=',pagerec.status_message)
    exit(1)
 print(len(recs),'Success: Page records read from',filein)
 return recs

def make_js(recs):
 outarr = []
 outarr.append('indexdata = [')
 arr = [] # array of Python dicts
 for rec in recs:
  d = rec.todict()  # a Python dictionary
  arr.append(d)
 return arr

def write_recs(fileout,data):
 with codecs.open(fileout,"w","utf-8") as f:
  f.write('indexdata = \n')
  jsonstring = json.dumps(data,indent=1)
  f.write( jsonstring +  '\n')
  f.write('; // end of indexdata\n')
  
 print('json data written to',fileout)

class PagerecsPreface:
 def __init__(self,epage,rpref,title):
  self.page = int(epage)
  self.ipage = rpref  # a string
  self.title = title 
  self.vpstr = '%03d' % epage
 def todict(self):
  e = {
   'page':int(self.page),
   'title':self.title,
   'ipage':self.ipage,
   'vp':self.vpstr
  }
  return e
  
def init_pagerecs_preface():
 recs = []
 ipref = 0  # 
 for epage in range(6,16):
  ipref = ipref + 1
  rpref = int_to_roman(ipref)
  rpref = rpref.lower()
  ipage = rpref
  title = 'praefatio %s' % rpref
  rec = PagerecsPreface(epage,rpref,title)
  recs.append(rec)
 # two additional pages before the first verse
 recs.append( PagerecsPreface(16,'1','1'))
 recs.append( PagerecsPreface(17,'2','2'))
 return recs

def init_pagerecs_prakrit():
 recs = []
 for ipage in range(75,94+1):
  epage = ipage + 15
  ipagestr = str(ipage)
  title = 'Page %s (prakrit)' % ipage
  recs.append(PagerecsPreface(epage,ipagestr,title))
 return recs

def init_pagerecs_VS():
 recs = []
 for ipage in range(95,108+1):
  epage = ipage + 15
  ipagestr = str(ipage)
  title = 'Page %s (Varietas scripturae)' % ipage
  recs.append(PagerecsPreface(epage,ipagestr,title))
 return recs

if __name__ == "__main__":
 filein=sys.argv[1]  # tab-delimited index file
 fileout = sys.argv[2]
 filevol = None
 
 pagerecs_main = init_pagerecs_main(filein,filevol=None)
 pagerecs_preface = init_pagerecs_preface()
 pagerecs_prakrit = init_pagerecs_prakrit()
 pagerecs_VS = init_pagerecs_VS()
 
 outrecs_main = make_js(pagerecs_main)
 outrecs_preface = make_js(pagerecs_preface)
 outrecs_prakrit = make_js(pagerecs_prakrit)
 outrecs_VS = make_js(pagerecs_VS)
 
 outrecs = (outrecs_preface + outrecs_main +
            outrecs_prakrit + outrecs_VS)
 write_recs(fileout,outrecs)
 #check1(pagerecs)
 
