
# outside of python:
# py manage.py graph_models -a > proj1.dot
# import subprocess
# subprocess.run(["python", "manage.py", "graph_models", "-a", ">", "proj6.dot"])

# then here call this to create a png of the graph. This doesnt work in the terminal according to pydot docs
# for some reason.
import pydot
# TODO: BEWARE OF PRINTS FROM REGULAR PYTHON THAT ARE RUN ON STARTUP OF MANAGE.PY
(graph, ) = pydot.graph_from_dot_file('proj6.dot')

graph.write_png('proj6.png')
