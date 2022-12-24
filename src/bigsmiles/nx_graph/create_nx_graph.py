import types

try:
    import networkx as nx
except ImportError:
    raise ImportError("To use this feature install networkx. (pip install networkx)")

from bigsmiles.bigsmiles import BigSMILES, StochasticObject, StochasticFragment, Branch, Bond, BondDescriptor, BondDescriptorAtom, Atom
from bigsmiles.nx_graph.draw_nx_graph import draw


def create_nx_graph(bigsmiles: BigSMILES) -> nx.Graph:
    """ Starting point for creating nx.graph"""
    graph = nx.Graph(attr={'bigsmiles': bigsmiles})
    graph.draw = types.MethodType(draw, graph)
    graph._added = set()

    for node in bigsmiles.nodes:
        add_obj(graph, node)

    add_rings(graph, bigsmiles.rings)

    del graph._added
    return graph


remove_attr = {
    Atom: {"id_", "bonds"},
    Bond: {"atom1", "atom2"},
    BondDescriptor: {}
}


def get_obj_attr(obj: Atom | Bond | BondDescriptor) -> dict:
    """ Creates dict of attributes for object. """
    dict_ = {s: getattr(obj, s) for s in obj.__slots__ if hasattr(obj, s)}
    for attr in remove_attr[type(obj)]:
        if attr in dict_:
            del dict_[attr]

    return dict_


def add_rings(graph: nx.Graph, rings: list[Bond]):
    for ring in rings:
        add_bond(graph, ring)


def add_atom(graph: nx.Graph, atom: Atom) -> str:
    label = f"{atom.symbol}{atom.id_}"
    if graph.has_node(label):
        return label

    # graph.add_node(label, **get_obj_attr(atom))
    # for bond in atom.bonds:
    #     add_bond(graph, bond)

    return label


def add_bond(graph: nx.Graph, bond: Bond):
    atom1_label = add_obj(graph, bond.atom1)
    atom2_label = add_obj(graph, bond.atom2)
    if graph.has_edge(atom1_label, atom2_label):
        return

    graph.add_edge(atom1_label, atom2_label, **get_obj_attr(bond))


def add_bonding_descriptor_atom(graph: nx.Graph, bond_descr: BondDescriptorAtom) -> str:
    return add_bonding_descriptor(graph, bond_descr.descriptor)


symbol_remap = {
    "<": "<>",
    ">": "<>",
    "$": "$$"
}


def add_bonding_descriptor(graph: nx.Graph, bond_descr: BondDescriptor) -> str:
    label = f"{symbol_remap[bond_descr.symbol]}{bond_descr.index_}" + "\n{}" + str(bond_descr.stochastic_object.id_)
    if graph.has_node(label):
        return label

    graph.add_node(label)

    return label


def add_branch(graph: nx.Graph, branch: Branch):
    for node in branch.nodes:
        add_obj(graph, node)


def add_stochastic_object(graph: nx.Graph, stoch_obj: StochasticObject) -> str:
    #TODO: add implict

    if stoch_obj in graph._added:
        return add_bonding_descriptor(graph, stoch_obj.end_group_right.descriptor)

    # add bonding descriptors
    for bond_descr in stoch_obj.bonding_descriptors:
        add_bonding_descriptor(graph, bond_descr)

    for stoch_frag in stoch_obj.nodes:
        add_stochastic_fragment(graph, stoch_frag)

    # connect bonding descriptions to existing graph
    graph.add_edge(
        add_bonding_descriptor(graph, stoch_obj.end_group_right.descriptor),
        add_obj(graph, stoch_obj.bond_right.atom2)
    )
    graph._added.add(stoch_obj)
    return add_bonding_descriptor(graph, stoch_obj.end_group_left.descriptor)


def add_stochastic_fragment(graph: nx.Graph, stoch_frag: StochasticFragment):
    for node in stoch_frag.nodes:
        add_obj(graph, node)

    add_rings(graph, stoch_frag.rings)


obj_func = {
    Atom: add_atom,
    StochasticObject: add_stochastic_object,
    # StochasticFragment: add_stochastic_fragment,   # called from stochastic object
    Branch: add_branch,
    BondDescriptorAtom: add_bonding_descriptor_atom,
    Bond: add_bond
}


def add_obj(graph, obj: Atom | StochasticObject) -> str:
    return obj_func[type(obj)](graph, obj)
