import xml.parsers.expat
import re

class JUnitResults:
    def __init__(self, filename) -> None:
        self.results = []
        self.read(filename)
    
    def read(self, filename):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        with open(filename, "rb") as file:
            p.Parse(file.read())

    def start_element(self, name, attrs):
        if name == 'testcase':
            self.wip = attrs
        if name == 'failure':
            self.wip['failure'] = attrs
            self.wip['failure']['body'] = ""

    def end_element(self, name):
        if name == 'testcase':
            m = re.search(r'[a-zA-Z/[_]+config_([a-zA-Z]{2})[a-zA-Z/.\-_]+([0-9]+)[a-zA-Z/.-_]+',
                          self.wip['name'])
            self.wip['locality'] = m.group(1).upper()
            self.wip['test'] = m.group(2)
            self.wip['passed'] = 'failure' not in self.wip  
            self.results.append(self.wip)
            self.wip = None

    def char_data(self, data):
        self.wip['failure']['body'] += repr(data)

if __name__=='__main__':
    junit = JUnitResults('static/test_results.xml')
    print(junit.results)