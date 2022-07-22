import re
import uuid

def remove_hex_from_string(str):
   """Remove hex value from input string
   """
   return re.sub(r'[^\x00-\x7f]',r'', str)


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
