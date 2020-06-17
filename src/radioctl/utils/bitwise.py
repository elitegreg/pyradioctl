def bit_or(bitset):
    r = 0
    for bit in bitset:
        r |= int(bit)
    return r
