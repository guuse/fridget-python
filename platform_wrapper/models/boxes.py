from .box import Box


class Boxes(object):

    boxes = []

    def add_box(self, box: Box):
        self.boxes.append(box)

    def boxes_length(self):
        return len(self.boxes)
