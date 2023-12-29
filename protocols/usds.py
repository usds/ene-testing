# USDS format is exactly the native YAML format rendered in JSON
# this transformer passes the object through unchanged

class USDS:
    def produce(data):
        return data
    def consume(data):
        return data