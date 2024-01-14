def split_list_into_chunks(l, nchunks):
    for i in range(nchunks):
        yield l[i::nchunks]
