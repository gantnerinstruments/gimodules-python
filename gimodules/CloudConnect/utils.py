import re

def remove_hex_from_string(str):
   """Remove hex value from input string
   """
   return re.sub(r'[^\x00-\x7f]',r'', str)
