from graphviz import Digraph
import sys

# TODO: statement recognition : differentiate if from else if from else...
# TODO: handle else if and else. 
# TODO: Make conditionals point to what's next to them.
# TODO: Handle for loops.

def main(code_file, export_file):
    # open the file
    with open(code_file, "r") as f:
        code = f.readlines()

    # get the graph
    graph = []
    get_graph(0, [], code, graph)
    
    # visualize the graph
    dot = Digraph()
    for node_pair in graph:
        if len(node_pair) == 2:
            dot.edge(f"Line #{node_pair[0]+1}", f"Line #{node_pair[1]+1}")
    
    dot.render(export_file, view=True)

def get_graph(index, branch, code, graph):
    """
    Recursively converts the nested code to a graph
    """
    # base case 
    if index > len(code)-1:
        return index

    # terminate recurtion instance with a return value
    if "}" in code[index]:
        ## link the next line to the pervious neighbouring parent node
        # the line which represents the neighbour is one line brefore the branching point
        neighbouring_node = branch[-1]-1
        next_index = index+1

        if next_index < len(code):
            # check if next line isn't } 
            if "}" not in code[next_index]:
                graph.append([neighbouring_node, next_index])

        ## return the current line to set the parent method's local index
        return index

    # branch to a new instance 
    elif "{" in code[index]:   
        index = get_graph(index+1, branch+[index], code, graph)
    
    else:
        # connect the node to the previous & make a space for the next
        
        if graph:
            # connect
            if len(graph[-1]) < 2:
                graph[-1].append(index)

            # add
            graph.append([index])

        else:
            # add first node
            graph.append([index])

    ## will execute after branching
    # walk in a sequence    
    index = get_graph(index+1, branch, code, graph)
    # return the current line to set the parent method's local [i]
    return index

if __name__ == "__main__":
    if len(sys.argv) == 3:
        code_file = sys.argv[1]
        export_file = sys.argv[2]
        main(code_file, export_file)
    else:
        print("Usage: `python3 mkchr.py [c# code file location] [exported file location]`")