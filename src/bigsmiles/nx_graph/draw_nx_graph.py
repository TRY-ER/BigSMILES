
try:
    import networkx as nx
except ImportError:
    raise ImportError("To use this feature install networkx. (pip install networkx)")
try:
    import matplotlib.pyplot as plt
except ImportError:
    raise ImportError("To use this feature install matplotlib. (pip install matplotlib)")


colors = {
    "C": (0,0,0),
    "O": (199/255, 41/255,  24/255),
    "N": (8/255, 138/255, 28/255),
    "S": (205/255, 212/255, 8/255),
    "{": (137/255, 8/255, 212/255),
    ">": (137/255, 8/255, 212/255),
    "<": (137/255, 8/255, 212/255),
    "$": (137/255, 8/255, 212/255),
}


def get_atom_colors(graph) -> list:
    atom_colors = []

    for node in graph.nodes:
        if node[0] in colors:
            atom_colors.append(colors[node[0]])
        else:
            atom_colors.append(colors["C"])

    return atom_colors


def draw(self: nx.Graph):
    plt.close()
    plt.ylim([-1.1, 1.1])
    plt.xlim([-1.1, 1.1])
    plt.axis('off')
    nx.draw_networkx(self, pos=nx.kamada_kawai_layout(self),
                     node_size=300,
                     node_color=get_atom_colors(self),
                     width=6,
                     with_labels=True,
                     font_size=7,
                     font_color="w",
                     font_family="Arial Rounded MT Bold"
                     )
    plt.show()
