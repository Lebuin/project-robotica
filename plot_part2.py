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
    means = [sum(sorted(d)[:-0]) / (len(d)-0) for d in data]
    return data, means

folder = 'data/'
names = ['R1', 'R1 (autonome)', 'R2', 'R2 (autonome)']
colors = ['b', 'r', 'g', 'y']
data, means = get_data(folder+'part2')
for i in range(len(data)):
    plt.plot(
        [i+1 for k in range(len(data[i]))],
        data[i],
        '.',
        color=colors[i],
        label=names[i]
    )
    plt.plot(
        i+1,
        means[i],
        'x',
        color=colors[i],
        markersize=10
    )

plt.xlim((0, len(data)+1))
plt.tick_params(
    axis='x',
    which='both',
    bottom='off',
    top='off',
    labelbottom='off'
)
plt.legend(loc='upper left')
plt.title('part 2')
plt.show()
