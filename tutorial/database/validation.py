
data_fs = [('setup', '{"arm": "kinova gen3", "gripper": "robotiq 2f85", "camera": "intel d435"}'),
           ('image', 'image_data yooo')]

validation_dict = {"measurement": {"setup", "grasp", "entries", "sensor_outputs", "object_instance"}}
validation_dict_types = {str: {set: str}}

pose_types = {str: {list: {float, int}}}
test_pose = {"rotation": [1.0, 1.0, 1.0], "position": [1.0, 1.0, 1.0]}

measurement_keys = {"setup", "sensor_outputs", "grasp", "object_instance"}
measurement_entry_keys = {"type", "repository", "values", "name"}
entry_value_keys = {"name": {str, }, "probability": {float, int}, "value": {float, int}, "units": {str, }}
entry_value_key_groups = ({"name", "probability"}, {"name", "value", "std", "units"}, )
request_keys = {"measurement": measurement_keys, "entry": measurement_entry_keys}
# object_instance_keys = {"instance_id", "dataset"}
object_instance_conditions = {"dataset_id": {"dataset"}}


entry_top_level_keys = {"type", "measurement_id", "repository", "values"}
entry_types = {"continuous", "size", "categorical", "other"}
entry_value_types = {"name": {str, }, "value": {float, int}, "units": {str, }, "std": {int, float}, "other": {str, }, "probability": {float, int}}


def check_key_existences(the_dict: dict, the_requirements):
    the_keys = the_dict.keys()
    if type(the_requirements) == tuple or type(the_requirements) == list:
        res = 0
        for one_requirement in the_requirements:
            res += check_key_existences(the_dict, one_requirement)
        return res > 0
    elif type(the_requirements) == dict:
        the_required_keys = set(the_requirements.keys())
        return len(the_required_keys & the_keys) == len(the_required_keys)  # just one level down atm
    else:
        the_required_keys = set(the_requirements)  # set to set: sanity check
        return len(the_required_keys & the_keys) == len(the_required_keys)  # just one level down atm


def check_set_conditions(the_set: set, prereq: dict):
    prereq_keys = set(prereq.keys())
    for prereq_key in prereq_keys:
        if prereq_key in the_set:
            prereq_value = prereq[prereq_key]
            if len(prereq_value & the_set) != len(prereq_value):
                return False
    return True


def check_data_types(the_dict, template_dict):
    assert type(the_dict) == dict, "the_dict variable must be of type dict"
    assert type(template_dict) == dict, "template_dict variable must be of type dict"
    for k in template_dict:
        if k not in the_dict:
            continue
        if type(the_dict[k]) == template_dict[k]:
            continue
        if type(template_dict[k]) != dict:
            if type(the_dict[k]) in template_dict[k]:
                continue
            else:
                return False
        else:
            if not check_data_types(the_dict[k], template_dict[k]):
                return False
    return True


def check_data_types_uniform(the_object, type_dict):
    # assert type(the_dict) == dict, "the_dict variable must be of type dict"
    assert type(type_dict) == dict, "template_dict variable must be of type dict"
    if type(the_object) == set:
        the_new_object = list(the_object)
    else:
        the_new_object = the_object
    the_new_object_type = type(the_new_object)
    the_object_type = type(the_object)
    if the_new_object_type == dict:
        for k in the_new_object:
            k_type = type(k)
            if k_type not in type_dict:
                # print("if k_type not in type_dict:")
                return False
            elif type(type_dict[k_type]) == dict:
                if not check_data_types_uniform(the_new_object[k], type_dict[k_type]):
                    return False
            elif type(type_dict[k_type]) == set:
                if type(the_new_object[k]) not in type_dict[k_type]:
                    return False
            else:
                if type(the_new_object[k]) != type_dict[k_type]:
                    # print("type(the_dict[k]) != type_dict[k_type]:", type(the_new_object[k]), type_dict[k_type])
                    return False
                elif type(the_new_object[k]) in {dict, list, tuple, set} and type(type_dict[k_type]) == dict:
                    if not check_data_types_uniform(the_new_object[k], type_dict[k_type]):
                        return False
    else:
        for i in range(len(the_new_object)):
            if type(type_dict[the_object_type]) == set:
                if type(the_new_object[i]) not in type_dict[the_new_object_type]:
                    # print("type(the_dict[i]) not in type_dict[type(the_dict)]", type(the_new_object[i]), type_dict[the_new_object_type])
                    return False
            else:
                if type(the_new_object[i]) != type_dict[the_object_type]:
                    return False
                if type(the_new_object[i]) in {dict, list, tuple, set} and type(type_dict[type(the_new_object[i])]) == dict:
                    if not check_data_types_uniform(the_new_object[i], type_dict[type(i)]):
                        return False
    return True


def check_measurement_request(request_dict):
    for i in request_keys:
        print(i)
        if i not in request_dict:
            return i
        for j in request_keys[i]:
            if j not in request_dict[i]:
                return j+" in "+i
    for k, i in enumerate(request_dict["entry"]["values"]):
        is_ok = False
        missing_stuff = None
        for g in entry_value_key_groups:
            ks = set(i.keys())
            if not is_ok:
                if len(g & ks) != len(g):
                    missing_stuff = str(g - ks)
                else:
                    is_ok = True
        if not is_ok:
            return missing_stuff
        # for j in entry_value_keys:
        #     if j not in i:
        #         return j + " in " + "entry.values["+str(k)+"]"
    print("measurement ok")


def check_entry_request(request_dict):
    for i in entry_top_level_keys:
        if i not in request_dict:
            return i
    for k, i in enumerate(request_dict["values"]):
        for j in entry_value_keys:
            if j not in i:
                return j + " in " + "entry.values["+str(k)+"]"
    print("entry ok")


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


if __name__ == "__main__":
    mydict = {"name": "lolname", "probability": 0.5}
    wrongdict = {"name2": "lolname", "probability": 0.5}
    contdict = {"name": 1, "value":2, "std":2, "units":2}
    print(mydict, check_key_existences(mydict, entry_value_key_groups))
    print(wrongdict, check_key_existences(wrongdict, entry_value_key_groups))
    print(contdict, check_key_existences(contdict, entry_value_key_groups))

    preqdict1 = {"dataset_id": 1}
    preqdict2 = {"dataset_id": 2, "dataset": 2}
    print(set(preqdict1.keys()), check_set_conditions(set(preqdict1.keys()), object_instance_conditions))
    print(set(preqdict2.keys()), check_set_conditions(set(preqdict2.keys()), object_instance_conditions))

    entry_val = {"name": "this is a string", "probability": 0.5, "value": 0.5, "units": "another string"}
    entry_val_wrong = {"name": 0.5, "probability": 0.5, "value": 0.5, "units": "another string"}
    print(entry_val, entry_value_types, check_data_types(entry_val, entry_value_types))
    print(entry_val_wrong, entry_value_types, check_data_types(entry_val_wrong, entry_value_types))

    print(validation_dict, validation_dict_types, check_data_types_uniform(validation_dict, validation_dict_types))

    print(test_pose, pose_types, check_data_types_uniform(test_pose, pose_types))
