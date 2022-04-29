
# outside of python:
# py manage.py graph_models -a > proj1.dot
# import subprocess
# subprocess.run(["python", "manage.py", "graph_models", "-a", ">", "proj9.dot"])

# then here call this to create a png of the graph. This doesnt work in the terminal according to pydot docs
# for some reason.
import pydot
# TODO: BEWARE OF PRINTS FROM REGULAR PYTHON THAT ARE RUN ON STARTUP OF MANAGE.PY
abs_path = r'/main\proj9.dot'
abs_target_path = r'/main\proj9.png'
with open(abs_path, mode='r', encoding='utf-8', errors='replace') as fp:
    # print(fp.readlines())
    k = 0
    rd = fp.read()
    my_str = rd
    while True:
        finished = True
        for i in my_str:
            ordi = ord(i)
            if not 0 < ordi < 128:
                # print(len(my_str))
                my_str = my_str.replace(i, '')
                # print(len(my_str))
                finished = False
                break
        if finished:
            break
    # print(fp.read())
    (graph, ) = pydot.graph_from_dot_data(my_str)
    # (graph, ) = pydot.graph_from_dot_file(abs_path)

graph.write_png(abs_target_path)
svg_string = graph.create_svg().decode('utf-8')
print(svg_string)
