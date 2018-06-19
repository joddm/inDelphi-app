###############################################
# Functions and variables for URL shortening
###############################################

chars = None
dna_to_code = dict()
code_to_dna = dict()

KMER_LEN = 9

def __init_chars():
  global chars
  chars = [chr(s) for s in range(48, 48 + 10)] + [chr(s) for s in range(65, 65 + 26)] + [chr(s) for s in range(97, 97 + 26)]
  chars += ['-', '_', '~', '.']
  chars.remove('_')
  return

def __init_mappers():
  output = chars
  # All 3-mers of 65-length safe html character alphabet
  for idx in range(3-1):
    output = __append_alphabet(output, chars)
  triplets = output

  # All 9-mers DNA
  output = list('ACGT')
  for idx in range(KMER_LEN-1):
    output = __append_alphabet(output, list('ACGT'))
  kmers = output

  global dna_to_code
  global code_to_dna
  for kmer, triplet in zip(kmers, triplets):
    dna_to_code[kmer] = triplet
    code_to_dna[triplet] = kmer
  return

def __append_alphabet(output, alphabet):
  new_output = []
  for o in output:
    for a in alphabet:
      new_output.append(o + a)
  return new_output

def parse_valid_url_path_single(url_path):
  ## Expected format:
  # [code][ACGT*].[indexnumber of cutsite]
  print(url_path)
  if url_path[:len('/single_')] != '/single_':
    return False, None, None

  url_path = url_path.replace('/single_', '')
  print(url_path)
  if len(url_path) == 0 or '_' not in url_path:
    return False, None, None

  threeparts = url_path.split('_')
  print('a')
  if len(threeparts) != 3:
    return False, None, None

  [coded, leftover, tail] = threeparts

  # Process encoded DNA
  print('a')
  if len(coded) % 3 != 0:
    return False, None, None  

  print('a')
  seq = ''
  for jdx in range(0, len(coded), 3):
    w = coded[jdx : jdx + 3]
    seq += code_to_dna[w]

  print('a')
  # Process leftover eDNA
  if leftover != '-':
    seq += leftover


  print('a')
  # Process cutsite
  try:
    cutsite_index = int(tail)
  except:
    return False, None, None
  return True, seq, cutsite_index

def encode_dna_to_url_path_single(seq, cutsite):
  encodeddna = ''
  for idx in range(0, len(seq), KMER_LEN):
    chomp = seq[idx : idx + KMER_LEN]
    if len(chomp) == KMER_LEN:
      encodeddna += dna_to_code[chomp]
    else:
      break
  if len(seq[idx:]) != KMER_LEN:
    leftoverdna = seq[idx:]
  else:
    leftoverdna = '-'
  return '/single_%s_%s_%s' % (encodeddna, leftoverdna, cutsite)

__init_chars()
__init_mappers()

###############################################
# Compbio operations
###############################################

def revcomp(seq):
  rc_mapper = {'A': 'T', 'G': 'C', 'C': 'G', 'T': 'A'}
  rc_seq = []
  for c in seq:
    if c in rc_mapper:
      rc_seq.append(rc_mapper[c])
    else:
      rc_seq.append(c)
  return ''.join(rc_seq[::-1])

def pam_shift(text1, text2, text_pam, direction):
  seq = text1 + text2
  cutsite = len(text1)

  if direction == 'right':
    cutsites = range(cutsite + 1, len(seq))
  elif direction == 'left':
    cutsites = range(cutsite - 1, 0, -1)

  for ct in cutsites:
    candidate_pam = seq[ct + 3 : ct + 6]
    if match(text_pam, candidate_pam):
      return seq[:ct], seq[ct:]
  return None

mapper = {
  'A': list('A'),
  'C': list('C'),
  'G': list('G'),
  'T': list('T'),
  'Y': list('CT'),
  'R': list('AG'),
  'W': list('AT'),
  'S': list('GC'),
  'K': list('TG'),
  'M': list('AC'),
  'D': list('AGT'),
  'V': list('ACG'),
  'H': list('ACT'),
  'B': list('CGT'),
  'N': list('ACGT'),
}
def match(template, dna):
  if len(dna) != len(template):
    return False
  for char, t in zip(dna, template):
    if char not in mapper[t]:
      return False
  return True
