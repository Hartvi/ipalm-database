
data_fs = [('setup', '{"arm": "kinova gen3", "gripper": "robotiq 2f85", "camera": "intel d435"}'),
           ('image', 'image_data yooo')]

validation_dict = {"measurement": {"setup", "grasp", "entries", "sensor_outputs", "object_instance"}}


def get_first_items(data_fields):
    return set(map(lambda x: x[0], data_fields))


def validate_data_fields(request_items, model_name):
    if type(request_items) == dict:
        first_items = set(request_items.keys())
    else:
        first_items = get_first_items(request_items)
    validation_fields = validation_dict[model_name]
    # print("validation_fields:", validation_fields)
    # print("first_items:", first_items)
    return len(first_items.intersection(validation_fields)) == len(validation_fields), validation_fields - first_items


# print(get_first_items(data_fs))

