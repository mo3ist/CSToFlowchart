from graphviz import Digraph
import sys

# TODO: clean the code [comments, vars, funcs..]
# TODO: add delimiters for ture/false dirs
    # DONE => ture
# TODO: handle comments in-between rel ifs [& everywhere else rly]
# TODO: IMPORTANT improve delimiters that could be used anywhere else
    # DONE => '{' and '}'
# TODO: style
    # DONE
# TODO: escape string fed to graphviz
    # DONE
# TODO: support a whole working file
# TODO: line string processing 
# TODO: for loop support
    # DONE!

def main(code_file, export_file):
    # open the file
    with open(code_file, "r") as f:
        code = f.readlines()

    # get the graph
    graph = []
    code = for_to_while(code)
    get_graph(0, [], code, graph, [])
    visualize(graph, code, export_file)

def for_to_while(code):
    def convert(line):
        ## for (int i=0; i<10; i++)
        # get whats inside the parentheses
        inside = line.split("(")[1].split(")")[0]
        declaration, cond, delta = inside.split(";")
        return declaration, cond, delta 


    ## THE FAST (BUT BAD) FIX TO DO CONVERT NESTED FOR'S IS BY REPEATING UNTIL THERE'S NO FOR
        
    # get how many for's are in the code
    times = 0
    for l in code:
        if "for" in l:
            times += 1
    
    new_code = []
    for time in range(times):
        # reset stuff
        new_code = []
        stack = []
        got_for = False

        # search for a for and if you find it, find the last line in its block then do stuff
        for i, l in enumerate(code):
            if "for" in l and not got_for: 
                got_for = True
                declaration, cond, delta = convert(l)

                spaces = len(l) - len(l.strip())            
                while_line = " "*(spaces-1)+f"while ({cond})\n"

                spaces = len(l) - len(l.strip())
                new_code.append(" "*(spaces-1) + declaration+";\n")
                new_code.append(while_line)
                continue
            
            if got_for and "{" == l.strip():
                stack.append("{")
            
            elif got_for and "}" == l.strip():
                stack.pop()
                if not stack:
                    spaces = len(l) - len(l.strip())
                    new_code.append(" "*(spaces-1) + delta+";\n")
                    got_for = False

            new_code.append(l)
        
        # update code
        code = new_code
    return new_code if new_code else code

def visualize(graph, code, export_file):
    """
    Visualizes a given graph
    """
    # visualize the graph
    dot = Digraph("G")
    dot.attr(fontsize="5")

    # init the nodes and style them
    for i, l in enumerate(code):
        line = str(i+1) + "# " + l.strip()
        if not (l.strip() == "}" or l.strip() == "{"):
            if ("if" in l.split() or "else" in l.split()):
                dot.attr("node", shape="diamond", color="red")
            elif "while" in l.split():
                dot.attr("node", shape="diamond", color="green")
            else:
                dot.attr("node", shape="box", color="black")
            dot.node(line.replace("\\", "\\\\"))

    for node_pair in graph:
        if len(node_pair) > 1:
            label = f""
            if "True" in node_pair:
                label = "True"
            if node_pair[1] >= len(code):
                last = "END"
            else:
                last = str(node_pair[1]+1)+ "# " +code[node_pair[1]].strip().replace("\\", "\\\\")
            
            first = str(node_pair[0]+1)+ "# " +code[node_pair[0]].strip().replace("\\", "\\\\")
            
            # the formatting of first and last has to be identical because last in one pair
            # is likely to be first in another
            # and graphviz uses the text as an id of a node
            dot.edge(first, last,label = label)
    
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
        
        # when the last line is clear, connect it to end
        if "}" != code[index-1].strip():
            graph.append([index-1, len(code)])
        return index

    # terminate recursion instance with a return value
    if "}" == code[index].strip():
        # check if we're branching from an if  
        if if_tracker and branch[-1]-1 == if_tracker[-1][0]:
            ## link the rel ifs
            # neighbour is previous branch point
            neighbouring_branch = branch[-1]-1
            # if it's not }, connect the if with the coming, it will be either "else if/else" or
            # -if it's the last block- the next 'available'/'clear' line 
            
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
            
            # searching for the line
            next_index = None       # meaning there's no clear one, aka end
            if not in_loop:
                for l in range(index, len(code)):
                    if "}" != code[l].strip():
                        next_index = l
                        break
            else:
                # connect to the head or the next clear line
                if index+1 < len(code):
                    # clear line
                    if "}" != code[index+1].strip():
                        next_index = index+1
                    # non clear line
                    else:
                        next_index = branch[-2]-1 

            #### else doesn't have a false dir ####
            is_else = False
            if "else" in code[neighbouring_branch] and not "if" in code[neighbouring_branch]:
                is_else = True

            # add the false branch if not else
            if not is_else:
                if next_index:
                    graph.append([neighbouring_branch, next_index])
                # no clear line but in loop
                elif not next_index and in_loop:
                    graph.append([neighbouring_branch, branch[-2]-1])
                else:
                    graph.append([neighbouring_branch, len(code)])

            ## add the last line in the block to the if_tracker
            
            # //code.cs//
            # if
            # {
            # ...
            #    }   => this can't be last line
            # }  
                
            if "}" != code[index-1].strip():
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
                                    if "}" != line.strip():
                                        l = i+index+1
                                        break
                            else:
                                # the line would be the head of the loop
                                # IF THERE'S NO CLEAR NEXT LINE!
                                
                                if "}" != code[index+1].strip():
                                    # clear line
                                    l = index + 1
                                else:
                                    # no clear line
                                    l = branch[-2]-1 

                            # check if the line isn't a non-clear-line
                            if popped[1]:
                                if l != None: # you have to specify None here cause l can be == 0
                                    graph.append([popped[1], l])
                                else:
                                    graph.append([popped[1], len(code)])                                    


        # if we're in a loop
        elif "while" in code[branch[-1]-1]:
            ## true direcion
            # find a clear last line
            if "}" != code[index-1].strip():
                graph.append([index-1, branch[-1]-1]) 
            else:
                pass

            # false direction
            # search for next line
            next_line = None
            for l in range(index+1, len(code)):
                if "}" != code[l].strip():
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
    elif "{" == code[index].strip():   

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
            if len(graph) > 1:
                # NOTE: since the delimiter is "{" instead of the keyword itself, 
                # the "if" line is alone in the graph as well as its previous line
                # so the line before "if" is graph[-2]
                # NOTE: you must make sure that the previous line ins't a '}' delimiter
                # if it was, then the linkage would've been already done in the 'rel if' stuff 
                prev_line = graph[-1][0]-1
                if "}" != code[prev_line].strip():
                    graph[-2].append(index-1)

                ## ADD THE TRUE DIR DELIMITER
                # if this is the first line in true branch and not a successor to a normal line
                if graph[-2][0]+1 in branch:   
                    graph[-2].append("True")


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
                if "}" != code[index-2].strip():
                    if "{" != code[index-2].strip():
                        # were under a niormal line 
                        graph.append([index-2, index-1])
                    else:
                        #- {        // nested
                        #     while
                        #     {     // current line
                        #       
                        # that means we're under a nested block
                        graph.append([index-3, index-1])

                        # ADD TRUE DIR DELIMITER
                        graph[-1].append("True")

            # add current line to graph so that next line will attach to it
            graph.append([index-1])

            # ## ADD THE TRUE DIR DELIMITER [if while was after a branch]
            # # if this is the first line in true branch and not a successor to a normal line
            # if graph[-2][0]+1 in branch:   
            #     graph[-2].append("True")


        branch += [index]
        index = get_graph(index+1, branch, code, graph, if_tracker)
    else:
        # connect the node to the previous & make a space for the next
        
        if graph:
            # connect
            if len(graph[-1]) < 2:
                # check that the node we'll conenct to is a normal line IN THE SCOPE
                
                if index < len(code)-1:
                    if "{" != code[index + 1].strip():
                        graph[-1].append(index)
                        
                        ## ADD THE TRUE DIR DELIMITER
                        # if this is the first line in true branch and not a successor to a normal line
                        if graph[-1][0]+1 in branch:   
                            graph[-1].append("True")
            

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