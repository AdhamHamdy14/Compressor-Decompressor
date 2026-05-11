MIN_MATCH = 3
MAX_MATCH = 258
WINDOW_SIZE = 32768
MAX_CANDIDATES = 64

def LZ77_compression(data: bytes):
    size = len(data)
    table = {}
    tokens = []
    i = 0

    while(i<size):
        if(i+MIN_MATCH > size):
            for j in range(i,size):
                tokens.append(("literal",data[j]))
            break
        x = data[i:i+3]

        best_len = 0
        best_dis = 0
        Candidates = table.get(x,[])

        for candidate in reversed(Candidates[-MAX_CANDIDATES: ]):
            distance = i-candidate
            if distance > WINDOW_SIZE:
                continue

            length = 0
            while( i+length <size and length<MAX_MATCH and data[i+length]==data[candidate+length]):
                length += 1

            if(length > best_len or (length==best_len and distance < best_dis)):
                best_len = length
                best_dis = distance

        if (best_len >= MIN_MATCH):
            tokens.append(("match", best_len, best_dis))
            for j in range(i,i+best_len):
                if j + MIN_MATCH <= size:
                    key = data[j:j+3]
                    table.setdefault(key,[]).append(j)
            i += best_len

        else:
            tokens.append(("literal",data[i]))
            table[x] = [i]
            i +=1


    return tokens
