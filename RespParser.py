'''
Parses and serializes based on RESP format.
'''

prefix_byte = {
    int : ':',
    str : '+',
}

class Incomplete(Exception):
    pass

class RespParser:
    def __init__(self):
        self.buffer = b''

    def feed(self, data: bytes):
        self.buffer += data 

    def get_command(self):
        if not self.buffer:
            return None
        try:
            value, self.buffer = self._parse(self.buffer)
            return value
        except Incomplete:
            return None
        
    def _parse(self, data: bytes):
        print(data)

        if len(data) < 3:
            raise Incomplete()

        data_type = chr(data[0])
        match (data_type):
            case '+':
                value, data = self._parse_simple_string(data)
                return value, data
            case ':':
                value, data = self._parse_int(data)
                return value, data
            case '$':
                value, data = self._parse_bulk_string(data)
                return value, data
            case '*':
                value, data = self._parse_array(data)
                return value, data
            
        return None

    def _read_line(self, data):
        index = data.find(b'\r\n')
        if index == -1:
            raise Incomplete()
        return data[1:index], data[index+2:]

    def _parse_simple_string(self, data):
        value, rest = self._read_line(data)
        return value, rest

    def _parse_int(self, data):
        value, rest = self._read_line(data)
        return int(value), rest

    def _parse_bulk_string(self, data):
        # $<length>\r\n<bytes>\r\n
        line, rest = self._read_line(data)
        length = int(line)
        if length == -1:  # NULL bulk string
            return None, rest
        
        if len(rest) < length + 2:
            raise Incomplete()
        value = rest[:length]
        rest = rest[length + 2:]
        return value, rest

    def _parse_array(self, data):
        # *<count>\r\n followed by that many RESP values
        line, rest = self._read_line(data)
        count = int(line)
        if count == -1:  # NULL array
            return None, rest
        items = []
        buf = rest
        for _ in range(count):
            if not buf:
                raise Incomplete()
            val, buf = self._parse(buf)
            items.append(val)
        return items, buf
