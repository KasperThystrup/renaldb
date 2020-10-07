"""
This is a simple function to handle forms which have a text input and file upload field.
"""


def resolvefileortext(input_text, file_input_key, request):
    """
    :param input_text:
    :param file_input_key:
    :param request:
    :param error_message:
    :return:
    """
    error_message = ""
    if input_text == "":
        if file_input_key in request.FILES:
            input_text = request.FILES[file_input_key].read()
        else:
            error_message = "Must submit file or text. No data submitted."
    else:
        if file_input_key in request.FILES:
            error_message = "Must submit file or text. Cannot accept both."

    return input_text, error_message