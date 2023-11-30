import sys

from matplotlib import axes
import networkx as nx


def draw_graph(table : list[list[float]], ax : axes.Axes, initial_state : int=0) -> None:
    edges = []
    labels = {}
    edge_labels = {}
    present = [False for _ in range(len(table))]

    for i, row in enumerate(table):
        for j, item in enumerate(row):
            if (sys.float_info.epsilon < abs(item)):
                edges.append([i, j])
                labels[i] = str(i)
                labels[j] = str(j)
                edge_labels[(i, j)] = item
                present[i] = True
                present[j] = True

    G = nx.DiGraph()
    G.add_edges_from(edges)

    colors = ["red" if initial_state == i else "blue" for i in G]

    pos = nx.kamada_kawai_layout(G)
    # pos = nx.spring_layout(G)

    ax.cla()

    nx.draw(G, pos, labels=labels, font_color="white", node_color=colors,
            connectionstyle="arc3,rad=0.1", ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, label_pos=0.45)


def draw_probabilities(probabilities : list[list[float]], step : float,
                       ax : axes.Axes) -> None:
    timeline = [i * step for i in range(len(probabilities))]

    ax.cla()

    for i in range(len(probabilities[0])):
        ax.plot(timeline, list(map(lambda x: x[i], probabilities)), label=str(i))

    ax.plot(timeline, list(map(sum, probabilities)), label="sum")

    ax.grid(True)
    ax.legend();

