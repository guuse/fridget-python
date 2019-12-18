from platform_wrapper.models.box import Box
from platform_wrapper.models.boxes import Boxes


def create_boxes_from_json(json_array):
    """Converts a json response of boxes to a Python object of Boxes

    :param json_array: a json array of boxes

    :returns: Boxes object
    """

    boxes = Boxes()

    for boxes_json_object in json_array:

        box_object = Box(
            box_id=boxes_json_object['id'],
            box_name=boxes_json_object['name'],
            box_desc=boxes_json_object['description']
        )

        boxes.add_box(box_object)

    return boxes
