def process_keypress_label(event, label, value: str, max_length: int = 16):
    """Append a keypress value to a QLabel

    2 special cases are present, delete and space

    :param event: A QMouseEvent, not required to be sent explicitly
    :param label: Reference to the QLabel
    :param value: The value of the keypress
    :param max_length: The max length of the text of the label, default 16
    """
    if value == 'space' and len(label.text()) < max_length:
        label.setText(label.text() + " ")
    elif value != 'delete' and len(label.text()) < max_length:
        label.setText(label.text() + value)
    elif value == 'delete' and len(label.text()) > 0:
        label.setText(label.text()[:-1])