
# outside of python:
# py manage.py graph_models -a > proj1.dot
import subprocess
subprocess.run(["python", "manage.py", "graph_models", "-a", ">", "proj1.dot"])

# then here call this to create a png of the graph. This doesnt work in the terminal according to pydot docs
# for some reason.
import pydot
(graph, ) = pydot.graph_from_dot_file('proj5.dot')

graph.write_png('proj5.png')
