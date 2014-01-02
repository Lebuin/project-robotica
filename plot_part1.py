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

values = {
    'map_size': [20, 15, 25, 30],
    'num_areas': [100, 70, 130, 160, 200],
    'num_colours': [10, 7, 15],
    'num_walls': [10, 7, 15],
    'num_particles': [100, 50, 70, 140, 190]
}

folder = 'data/'
names = ['R1', 'R2']
colors = ['b', 'r']
plot_number = 1

plt.subplot(2, 3, plot_number)
data, base_means = get_data(folder+'base_case')
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
        base_means[i],
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
plt.title('base_case')

for name in ['map_size', 'num_areas', 'num_colours', 'num_walls', 'num_particles']:
    data = [base_means]
    
    for i in range(1, len(values[name])):
        value = values[name][i]
        _, means = get_data(folder+name+str(value))
        if value < values[name][0]:
            data.insert(0, means)
        else:
            data.append(means)
    data = list(zip(*data))
    
    plot_number += 1
    plt.subplot(2, 3, plot_number)
    for i in range(len(data)):
        plt.plot(
            sorted(values[name]),
            data[i],
            color=colors[i],
            marker='+'
        )
    plt.ylim((0, 200))
    plt.title(name)

plt.show()
