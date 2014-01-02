#!/usr/bin/env python3

import matplotlib.pyplot as plt

def string_to_list(string):
    return [int(i) for i in string.split(',')]

def get_data(path):
    f = open(path)
    f.readline()
    data = []
    for line in f:
        data.append(string_to_list(line))
    data = list(zip(*data))
    means = [sum(sorted(d)[:-2]) / (len(d)-2) for d in data]
    return data, means

folder = 'data/'
data, means = get_data(folder+'part2')
