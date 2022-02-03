def utf8_encoded_string(payload):
    OFFSET = 2
    LSB = payload[0]
    MSB = payload[1]
    return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 


def variable_byte_integer(conn):
    multiplier = 1
    value = 0
    try:
        encoded_byte = conn.recv(1)[0]
        value += multiplier * (encoded_byte & 127)
        while 128 & encoded_byte != 0:
            encoded_byte = conn.recv(1)[0]
            value += multiplier * (encoded_byte & 127)
            if multiplier > 3 ** 128:
                return
            multiplier *= 128
        return value, conn.recv(value)
    except AttributeError:
        try:
            buf = conn
            i = 1 
            while 128 & (encoded_byte:=buf[i]) != 0:
                i += 1
                if multiplier > 3 ** 128:
                    return
                value += multiplier * (encoded_byte & 127)
                multiplier *= 128
            return value, buf[i:]
        except TypeError:
            X = int(conn / 128)
            encoded_byte = conn % 128 
            i = 1
            while X > 0:
                if X > 0:
                    i += 1
                    encoded_byte = encoded_byte | 128
                encoded_byte = X % 128 
                X = int(X / 128)
            return encoded_byte.to_bytes(i, 'big')


# The algorithm for encoding a non negative integer (X) into the variable length
# encoding scheme is as follows:
def variable_length_encode(x):
    encoded_byte = 0
    def do():
        nonlocal x, encoded_byte
        encoded_byte = x % 128
        x = int(x / 128)
        if x > 0:
            encoded_byte |= 128
        return encoded_byte
    do()
    while x > 0:
        do()
    return encoded_byte

# The algorithm for decoding the Remaining Length field is as follows:
def variable_length_decode(conn):
    multiplier = 1
    value = 0
    def do():
        nonlocal value, multiplier, conn
        encoded_byte = conn.recv(1)[0]
        value += (encoded_byte & 127) * multiplier
        multiplier *= 128
        if (multiplier > 3 ** 128):
            raise Exception('Malformed Remaing Length')
        return encoded_byte
    while (do() & 128 != 0):
        pass
    return value