from graphviz import Digraph
import sys

# BUG 1: the true branch of rel if statements doesn't link to the loop head if it was nested under it
# BUG 2: the last if statement points outside the loop if it was nested under it 
# TODO: clean the code [comments, vars, funcs..]
# TODO: add delimiters for true and false directions
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
        # deal with the level 0 branch's ifs
        while if_tracker:
            popped = if_tracker.pop()
            # if clear line 
            if popped[1] != None:
                graph.append([popped[1], len(code)])
        return index

    # terminate recursion instance with a return value
    if "}" in code[index]:
        # check if we're branching from an if  
        if if_tracker and branch[-1]-1 == if_tracker[-1][0]:
            ## link the rel ifs
            # neighbour is previous branch point
            neighbouring_branch = branch[-1]-1
            # if it's not }, connect the if with the coming, it will be either "else if/else" or
            # -if it's the last block- the next 'available'/'clear' line 
            
            # searching for the line
            next_index = None       # meaning there's no clear one, aka end
            for l in range(index, len(code)):
                if "}" not in code[l]:
                    next_index = l
                    break


            # NOTE: things will be different for the last block in the rel if statements
            # you see, if we were in a loop then the next line would be the head of the loop
            # NOT any line after.
            in_loop = False
            if index+1 < len(code):
                # if last line in rel ifs
                if not ("else" in code[index+1]):
                    if len(branch) > 1:
                        if "while" in code[branch[-2]-1]:
                            in_loop = True
            # count for being in a loop 
            if in_loop:
                next_index = branch[-2]-1

            if next_index:
                print(f"linking {neighbouring_branch}, {next_index}")
                graph.append([neighbouring_branch, next_index])
            else:
                graph.append([neighbouring_branch, len(code)])
            ## add the last line in the block to the if_tracker
            
            # //code.cs//
            # if
            # {
            # ...
            #    }   => this can't be last line
            # }  
                
            if "}" not in code[index-1]:
                if_tracker[-1].append(index-1)
            else :
                # no clear last line to the rel ifs
                # the last line will be the first non }
                if_tracker[-1].append(None) # none will be the indicator
                
                

                
            if index+1 < len(code):

                ## check if last rel if block
                next_line = code[index + 1].strip().split()
                if not ('else' in next_line):
                    # pop from the if_tracker
                    while if_tracker:

                        # when there's another nested block in the rel if 
                        # the last line in the if that the nested block is in won't be added yet
                        # so if_tracker will have no last line == (len == 1) 
                        if len(if_tracker[-1]) < 2:
                            break
                        else:
                            popped = if_tracker.pop()

                            # get the next available line
                            # it will be either after the current or before it [if it was in a loop]
                            
                            # check for a loop
                            in_loop = False
                            if len(branch) > 1:
                                if "while" in code[branch[-2]-1]:
                                    in_loop = True
                            
                            l = None
                            if not in_loop:
                                
                                for i, line in enumerate(code[index+1: ]):
                                    if "}" not in line:
                                        l = i+index+1
                                        break
                            else:
                                # the line would be the head of the loop
                                l = branch[-2]-1 

                            # check if the line isn't a non-clear-line
                            if popped[1]:
                                if l:
                                    graph.append([popped[1], l])
                                else:
                                    graph.append([popped[1], len(code)])                                    


        # if we're in a loop
        elif "while" in code[branch[-1]-1]:
            ## true direcion
            # find a clear last line
            if "}" not in code[index-1]:
                graph.append([index-1, branch[-1]-1]) 
            else:
                # ### SHIT:
                # # i need to loop in reverse to find a usable line then remove 
                # # it from the graph and link it to the head of the loop :)

                # # find the clear line
                # line = None
                # for i in range(index-1, branch[-1], -1):
                #     if "}" not in code[i]:
                #         line = i
                #         break
                
                # # pop it from graph with whatever it was linked to
                # for p in range(len(graph)-1, 0, -1):
                #     if graph[p][0] == line:
                #         graph.pop()
                        

                # # link it to the loop's head
                # graph.append([line, branch[-1]-1])
                pass

            # false direction
            # search for next line
            next_line = None
            for l in range(index+1, len(code)):
                if "}" not in code[l]:
                    next_line = l
                    break
            if next_line:
                graph.append([branch[-1]-1, next_line]) 
            else:
                graph.append([branch[-1]-1, len(code)]) 
    
        # pop the branch to keep track
        branch.pop()
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
            # if_tracker = []

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

        elif "while" in current_line:
            # link to previous line [IF NOT "}" -end of a nested block that will propably will be linked to this line
            # NOR "{"]
            if index-1 > 0:
                if "}" not in code[index-2]:
                    if "{" not in code[index-2]:
                        # were under a niormal line 
                        graph.append([index-2, index-1])
                    else:
                        # that means we're under a nested block
                        graph.append([index-3, index-1])
            # add current line to graph so that next line will attach to it
            graph.append([index-1])
        branch += [index]
        index = get_graph(index+1, branch, code, graph, if_tracker)
    else:
        # connect the node to the previous & make a space for the next
        
        if graph:
            # connect
            if len(graph[-1]) < 2:
                # check that the node we'll conenct to is a normal line IN THE SCOPE
                
                if index < len(code)-1:
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