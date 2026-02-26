'''
Parses and serializes based on RESP format.
'''

class Incomplete(Exception):
    pass

class RESPParser:
    def __init__(self):
        self.buffer = b''
    
    def feed(self, data: bytes):
        self.buffer += data 

    def get_command(self):
        if not self.buffer:
            return None
        try:
            value, self.buffer = parse_value(self.buffer)
            return value
        except Incomplete:
            return None

def parse_value(data: bytes):
    if len(data) < 3:
        raise Incomplete()

    data_type = chr(data[0])
    match (data_type):
        case '+':
            value, data = parse_simple_string(data)
            return value, data
        case ':':
            value, data = parse_int(data)
            return value, data
        
    return None

def read_line(data):
    index = data.find(b'\r\n')
    if index == -1:
        raise Incomplete()
    return data[1:index], data[index+2:]

def parse_simple_string(data):
    value, rest = read_line(data)
    return value, rest

def parse_int(data):
    value, rest = read_line(data)
    return int(value), rest

if __name__ == '__main__':
    rp = RESPParser()
    rp.feed(b'+OK\r\n:42\r\n')

    while (command := rp.get_command()) is not None:
        print(f'command: {command}')