#TODO endianess!!

def bcd_to_integer(bcd):
    result = 0
    mult = 1
    for byteval in bcd:
        lower = byteval & 0xF
        upper = (byteval & 0xF0) >> 4
        result += (upper * 10 + lower) * mult
        mult *= 100
    return result

def integer_to_bcd(i):
    result = b''

    while i > 0:
        a = i % 10
        i //= 10
        a |= (i % 10) << 4
        i //= 10
        result += bytes([a])

    return result

assert(integer_to_bcd(123456) == b'\x56\x34\x12')
