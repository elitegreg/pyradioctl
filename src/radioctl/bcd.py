def bcd_to_integer(bcd):
    result = 0
    mult = 1
    for byteval in bcd:
        lower = byteval & 0xF
        upper = (byteval & 0xF0) >> 4
        result += (upper * 10 + lower) * mult
        mult *= 100
    return result
