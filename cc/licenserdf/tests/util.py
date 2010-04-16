import copy

class PrinterCollector(object):
    def __init__(self):
        self.printed_strings = []

    def __call__(self, string):
        self.printed_strings.append(string)


def unordered_ensure_printer_printed(printer, expected_output):
    """
    Do an unordered check 
    """
    printer_output = copy.copy(printer.printed_strings)
    for line in expected_output:
        assert line in printer_output
        printer_output.pop(printer_output.index(line))

    # make sure that we only printed what we expected
    assert len(printer_output) is 0
