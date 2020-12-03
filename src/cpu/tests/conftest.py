

def pytest_assertrepr_compare(op, left, right):
    if op == "==":
        return ["0x{:02X} != 0x{:02X}".format(left, right)]
