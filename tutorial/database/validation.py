
data_fs = [('setup', '{"arm": "kinova gen3", "gripper": "robotiq 2f85", "camera": "intel d435"}'),
           ('image', 'image_data yooo')]

validation_dict = {"measurement": {"setup", "grasp", "entries", "sensor_outputs", "object_instance"}}

measurement_keys = {"setup", "sensor_outputs", "grasp", "object_instance"}
entry_keys = {"type", "repository", "values"}
entry_value_keys = {"name", "value", "units"}
request_keys = {"measurement": measurement_keys, "entry": entry_keys}
object_instance_keys = {"instance_id", "dataset"}

entry_types = {"continuous", "size", "categorical", "other"}


def check_measurement_request(request_dict):
    for i in request_keys:
        if i not in request_dict:
            return i
        for j in request_keys[i]:
            if j not in request_dict[i]:
                return j+" in "+i
    for k, i in enumerate(request_dict["entry"]["values"]):
        for j in entry_value_keys:
            if j not in i:
                return j + " in " + "entry.values["+str(k)+"]"


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

