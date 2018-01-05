import uuid

def create_uuid():
    return uuid.uuid4().hex

if __name__ == '__main__':
    a=create_uuid()
    print a