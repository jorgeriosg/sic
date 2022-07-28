import base64 as b64

# def csv_to_base64(path_file):
#     file = open("csv_to_base64.csv", "r").read()
#     encoded = b64.b64encode(file)
#     return encoded

def csv_to_base64(path_file):
    #file = open("csv_to_base64.csv", "r").read()
    encoded = b64.b64encode(path_file.getvalue().encode())
    return encoded