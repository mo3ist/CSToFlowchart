from graphviz import Digraph
import sys

# TODO: Handle loops.
# TODO: clean the code [comments, vars, funcs..]
def main(code_file, export_file):
    # open the file
    with open(code_file, "r") as f:
        code = f.readlines()

    # get the graph
    graph = []
    get_graph(0, [], code, graph, [])
    
    # visualize the graph
    dot = Digraph()
    for node_pair in graph:
        if len(node_pair) == 2:
            dot.edge(f"Line #{node_pair[0]+1}", f"Line #{node_pair[1]+1}")
    
    dot.render(export_file, view=True)

def get_graph(index, branch, code, graph, if_tracker):
    """
    Recursively converts the nested code to a graph
    """
    # base case 
    if index > len(code)-1:
        return index

    # terminate recurtion instance with a return value
    if "}" in code[index]:
        ## link the neighbouring socpes
        # neighbour is previous branch point
        neighbouring_node = branch[-1]-1
        next_index = index+1

        if next_index < len(code):
            # check if next line isn't } 
            if "}" not in code[next_index]:
                graph.append([neighbouring_node, next_index])

        ## connect the true branch of all rel if statements to the line after last rel if block 
        if index < len(code)-1: # not the last line

            # add the last line in the statement to the tracker 
            if if_tracker:
                ## if the current branch was an if statement
                # NOTE: potential index error
                if code[(branch[-1]-1)].strip().split()[0] in ["if", "else"]:
                    # add the previous line to if_tracker [end of 'true' branch]
                    if_tracker[-1].append(index - 1) 
                    
            # if last block
            next_line = code[index+1].strip().split()
            # no else's or if else's 
            if not ("else" in next_line or ("if" in next_line and ("else" in next_line))):
                # connect lines 
                for block in if_tracker:
                    graph.append([block[1], index+1])
        ## return the current line to set the parent method's local index
        return index

    # branch to a new instance 
    elif "{" in code[index]:   

        # We're in a new branch
        
        # NOTE: Potential index error 

        ## handle if statements
        ## since if's are related => (if, else if, else if, ..., else)
        ## in each block, if true, branch then go to after else' block
        ##            and if it's false then go to the next block
        ## so talking in terms of the algo here, what should be done
        ## is that we keep track of related if's then point 'true'
        ## post else' block 

        current_line = code[index-1].strip().split()

        # if
        if "if" in current_line and not "else" in current_line:
            
            # link the related if's blocks to the graph [the head 'if' to whatever is the prev normal line]
            if len(graph) > 2:
                # NOTE: since the delimiter is "{" instead of the keyword itself, 
                # the "if" line is alone in the graph as well as its previous line
                # so the line before "if" is graph[-2]
                # NOTE: you must make sure that the previous line ins't a '}' delimiter
                # if it was, then the linkage would've been already done in the 'rel if' stuff 
                prev_line = graph[-1][0]-1
                if "}" not in code[prev_line]:
                    graph[-2].append(index-1)
        
            # clear the tracker
            if_tracker = []

            # add a new rel if statement
            if_tracker.append([index-1])  

        # elif
        elif "else" in current_line and "if" in current_line :
            # add a new rel if statement
            if_tracker.append([index-1])  
        # else
        elif 'else' in current_line and 'if' not in current_line:
            # add a new rel if statement
            if_tracker.append([index-1])  
        branch += [index]
        index = get_graph(index+1, branch, code, graph, if_tracker)
    else:
        # connect the node to the previous & make a space for the next
        
        if graph:
            # connect
            if len(graph[-1]) < 2:
                # check that the node we'll conenct to is a normal line IN THE SCOPE
                
                if "{" not in code[index + 1]:
                    graph[-1].append(index)

            # add
            graph.append([index])

        else:
            # add first node
            graph.append([index])

    ## will execute after branching
    # walk in a sequence    
    index = get_graph(index+1, branch, code, graph, if_tracker)
    # return the current line to set the parent method's local [i]
    return index

if __name__ == "__main__":    
    if len(sys.argv) == 3:
        code_file = sys.argv[1]
        export_file = sys.argv[2]
        main(code_file, export_file)
    else:
        print("Usage: `python3 mkchr.py [c# code file location] [exported file location]`")