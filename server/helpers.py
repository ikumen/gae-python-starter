from flask.json import JSONEncoder

class JSONSerializable(object):
    def to_json(self):
        pass

class JSONSerializableEncoder(JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, JSONSerializable):
            return obj.to_json()
        return super(JSONSerializableEncoder, self).default(obj)