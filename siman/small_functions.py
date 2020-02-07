#Copyright Aksyonov D.A
from __future__ import division, unicode_literals, absolute_import 
import os, math, re, sys
import numpy as np
from collections import Iterable
import shutil, gzip
import traceback
from contextlib import contextmanager

try:
    from six import string_types
except:
    print('Warning! six module was not found, I use only str and basestring as string_types; errors can be expected')
    try:
        string_types = basestring #for python 2.7
    except NameError:
        string_types = str # for python 3

from siman import header
from siman.header import printlog



class TracePrints(object):
  def __init__(self):    
    self.stdout = sys.stdout
  def write(self, s):
    self.stdout.write("Writing %r\n" % s)
    traceback.print_stack(file=self.stdout)


def angle(v1, v2):
    #in degrees
    return math.acos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))) / math.pi * 180

def normal(v1, v2):
    #normal to two vectors
    return np.cross(v1, v2)


def red_prec(value, precision = 100.):
    #
    a = value * precision
    return round(a)/1./precision



def is_list_like(obj): 
    
	return not isinstance(obj, string_types) and isinstance(obj, Iterable)

def is_string_like(s):
    return isinstance(s, string_types)

def list2string(ilist, joiner = ' '):
    #' '.join(['{:}']*len(lis)).format(*lis)
    return joiner.join(np.array(ilist).astype(str))


def merge_dics(dic1, dic2):
	"""
	return dic
	"""
	dic_new = dic1.copy()
	dic_new.update(dic2)
	return dic_new


def cat_files(files, output_file):
    #files (list) - file names
    #

    with open(output_file,'wb') as wfd:
        for f in files:
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, wfd, 1024*1024*10)
    return


def grep_file(string, file, reverse = False):
    #reverse(bool) - read file in reversed order - require upload to memory
    out = ''
    lines = []
    with open(file, 'rb') as f:
        text = f.read().decode(errors='replace')
        # lines = f.readlines()
        lines = str(text).split('\n')
        # for line in text:
        # print(text)
        # print(lines)
        if reverse:
            f = reversed(lines)

        for line in f:
            # print(line)
            if string in line:
                out = line
                

    return str(out.strip() )

def gunzip_file(filename):
    printlog('unzipping file', filename)
    with open(filename[:-3], 'wb') as f_out:
        with gzip.open(filename, 'rb') as f_in:
            shutil.copyfileobj(f_in, f_out)

    return



def makedir(path):
    """
    *path* - path to some file 
    Make dirname(path) directory if it does not exist
    """
    dirname = os.path.dirname(path)

    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
        printlog("Directory", dirname, " was created", imp = 'y')
    return


def latex_chem(formula):
    """ """
    # print(formula)
    if '$' not in formula:
        formula =re.sub("([0-9]{1,3})", "$_{\\1}$", formula)
    return formula

def latex_spg(spg):

    # print(spg)
    # spg = spg.replace('_1', '$_1$')
    spg = spg.replace('p', 'P')
    if '-' in spg:
        pos = spg.find('-')
        dig = spg[pos+1]
        spg = spg.replace('-'+dig, '\\bar{'+dig+'}')
    spg = '$'+spg+'$'
    return spg


def bash_chk_file_cmd(file):
    #bash returns empty string if file exist
    return " [ -e "+   file     +""" ] || echo "NO"     ; """

# def find_transition_atom(elements):
#     #return list of unique transition elements
#     for elements

def get_common_chemical_base(st1,st2):
    from difflib import SequenceMatcher
    s1 = st1.get_reduced_formula()
    s2 = st2.get_reduced_formula()
    match = SequenceMatcher(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))
    base  = s1[match.a: match.a + match.size]
    return latex_chem(base)

def b2s(b):
    #bool to vasp str
    if b:
        s = 'T'
    else:
        s = 'F'

    return s


def is_unique(d, dist, prec = 0.001):
    """
    check if d is unique within the provided precision in the given list dist
    return 1 if unique, else 0 
    """

    if len(dist)>0: 
        if min([abs(d-d1) for d1 in dist])>prec:
            out = 1
        else:
            out = 0
    else:
        out = 1

    return out 


def calc_ngkpt(recip, kspacing):
    to_ang_local = 1
    
    N_from_kspacing = []
    for i in 0, 1, 2:
        N_from_kspacing.append( math.ceil( (np.linalg.norm(recip[i]) / to_ang_local) / kspacing) )

    return N_from_kspacing


def setting_sshpass(cl = None, clust = None):
    """
    Creates some variables for sshpass mode
    cl (Caluculation) - object, should contain cluster dict, has higher priority
    clust (dict) - cluster dicts
    """

    if cl and hasattr(cl , 'cluster'):
        clust = cl.cluster

    if 'sshpass' in clust and clust['sshpass']:
        printlog('setting sshpass to True', imp = '')
        header.sshpass = clust['sshpass']
        header.path2pass = clust['path2pass']
    else:
        header.sshpass = None
        header.path2pass = None



# def format_str():

@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)
