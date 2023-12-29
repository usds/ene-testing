# USDS format is exactly the native YAML format rendered in JSON
# this transformer passes the object through unchanged

def transform(data):
    return data