def dfs(graph, start, visited=None):
    """
    Depth-First Search algorithm implementation.
    
    Args:
        graph: A dictionary representing the adjacency list of the graph
        start: The starting vertex for the search
        visited: A set to keep track of visited vertices
        
    Returns:
        A list of vertices in the order they were visited
    """
    if visited is None:
        visited = set()
    
    result = [start]
    visited.add(start)
    
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    
    return result


def dfs_iterative(graph, start):
    """
    Iterative implementation of Depth-First Search algorithm.
    
    Args:
        graph: A dictionary representing the adjacency list of the graph
        start: The starting vertex for the search
        
    Returns:
        A list of vertices in the order they were visited
    """
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        print(stack)
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            # Add neighbors in reverse order to simulate recursive DFS
            for neighbor in reversed(graph.get(vertex, [])):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result
