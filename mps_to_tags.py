import pysmps.smps_loader as smps
import pysmps
import numpy as np
from os.path import getsize


'''
    Preprocessing variables types.
    If variable is integer and its boundries are: low=0, up=0
    --- then it is binary  
'''


def preprocessing_variables_types(mps_decoded):
  binaries = []
  integrals = []
  continious = []
  temp_zip = zip(
      range(0, len(mps_decoded['vt'])),
      mps_decoded['bnds']['LO'],
      mps_decoded['bnds']['UP'],
  )
  for i, l_bnd, u_bnd in temp_zip:
    if (mps_decoded['vt'][i] == "integral") and (l_bnd == 0) and (u_bnd == 1):
      mps_decoded['vt'][i] = "binary"
      binaries.append(i)
    elif mps_decoded['vt'][i] == "integral":
      integrals.append(i)
    else:
      continious.append(i)
  return binaries, integrals, continious


'''
  Function takes path to mps file
  It returns dictionary with tags and number of constraint which
  are similar to it 
'''

def mps_to_tags(path, count_large: bool = False):
  if not count_large:
    size = getsize(path)
    if size > 1024 * 1024: # experiments showed that colab handle with these files in 2 hours. That is rather slow for testing
      return 'large'
  mps = pysmps.smps_loader.load_mps(path)
  ''' 
    all constraints can be writen like:
      constraint_matrix * variables {inequality_sign} right_hand_sides
  '''
  mps_decoded = {
      'vt': mps[4], # variable types
      'bnds': None, # mps[11][bnd_keys[0]], # boundries
      'cm': mps[7], # constraint matrix
      'rhs': None, # right-hand sides
      'is': mps[5], # inequality signs
  }
  if not mps[9]:
    mps_decoded['rhs'] = np.array([0] * len(mps[5]))
  else:
    rhs_keys = list(mps[9].keys())
    mps_decoded['rhs'] = mps[9][rhs_keys[0]]
  if not mps[11]:
    mps_decoded['bnds'] = {'LO': np.array([0] * len(mps[4])),'UP': np.array([np.inf] * len(mps[4]))}
  else:
    bnd_keys = list(mps[11].keys())
    mps_decoded['bnds'] = mps[11][bnd_keys[0]]

  answer_tags = {
      "Singleton": 0,
      "Aggregation": 0,
      "Precedence": 0,
      "Variable Bound": 0,
      "Set Partitioning": 0,
      "Set Packing": 0,
      "Set Covering": 0,
      "Cardinality": 0,
      "Invariant Knapsack": 0,
      "Equation Knapsack": 0,
      "Binpacking": 0,
      "Knapsack": 0,
      "Integer Knapsack": 0,
      "Mixed Binary": 0,
      "General Linear": 0,
  }
  '''
    Preprocessing variables types.
    If variable is integer and its boundries are: low=0, up=0
    --- then it is binary  
  '''
  binaries, integrals, continious = preprocessing_variables_types(mps_decoded)
  temp_zip = zip(
      mps_decoded['cm'],
      mps_decoded['rhs'],
      mps_decoded['is'],
  )
  for line, rhv, sign in temp_zip:  # rhv --- right-hand value
    null_int_coef = True  # True if all integer coefficients are 0
    for i in integrals:
      if line[i] != 0:
        null_int_coef = False
    null_cont_coef = True # True if all continious coefficients are 0
    for i in continious:
      if line[i] != 0:
        null_cont_coef = False
    unit_bin_coef = True  # True if all binaries coefficients are 1
    for i in binaries:
      if (line[i] != 1) and (line[i] != 0):
        unit_bin_coef = False
    null_bin_coef = True # True if all binaries coefficients are 0
    for i in binaries:
      if line[i] != 0:
        null_bin_coef = False
    non_null = 0  # coefficients which are not 0
    for elem in line:
      if elem != 0:
        non_null += 1
    if non_null == 1:
      answer_tags['Singleton'] += 1
    elif non_null == 2:
      if sign == 'E':
        answer_tags['Aggregation'] += 1
      elif sign == 'L':
        a, b = 0, 0
        flag = True
        for i, elem in zip(range(len(line)), line):
          if (elem != 0):
            if flag:
              a = elem
              a_type = mps_decoded['vt'][i]
              flag = False
            else:
              b = elem
              b_type = mps_decoded['vt'][i]
        if (a == -b) and (b_type == a_type):
          answer_tags['Precedence'] += 1
        elif (a_type == 'binary') or (b_type == 'binary'):
          answer_tags['Variable Bound'] += 1
        elif null_int_coef and (sign != 'G'):
          answer_tags['Mixed Binary'] += 1
        else:
          answer_tags['General Linear'] += 1
      else:
        answer_tags['General Linear'] += 1
    elif null_int_coef and null_cont_coef and unit_bin_coef:
      if rhv == 1:
        if sign == 'E':
          answer_tags['Set Partitioning'] += 1
        elif sign == 'G':
          answer_tags['Set Covering'] += 1
        elif sign == 'L':
          answer_tags['Set Packing'] += 1
      elif (rhv >= 2) and (sign == 'E'):
        answer_tags['Cardinality'] += 1
      elif (rhv >= 2) and (np.modf(rhv)[0] == 0) and (sign == 'L'):
        answer_tags['Invariant Knapsack'] += 1
      elif sign != 'G':
        answer_tags['Mixed Binary'] += 1
      else:
        answer_tags['General Linear'] += 1
    elif null_int_coef and null_cont_coef and (rhv >= 2) and (np.modf(rhv)[0] == 0):
      if sign == 'E':
        answer_tags['Equation Knapsack'] += 1
      elif sign == 'L':
        binpacking = False # if constraint is binpacking
        for i in binaries:
          if line[i] == rhv:
            binpacking = True
        if binpacking:
          answer_tags['Binpacking'] += 1
        else:
          answer_tags['Knapsack'] += 1
    elif null_cont_coef and null_bin_coef and (sign == 'L') and (np.modf(rhv)[0] == 0):
      answer_tags['Integer Knapsack'] += 1
    elif null_int_coef and (sign != 'G'):
      answer_tags['Mixed Binary'] += 1
    else:
      answer_tags['General Linear'] += 1
  return answer_tags
