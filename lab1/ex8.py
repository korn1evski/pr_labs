import re

class CustomSerializer:
    @staticmethod
    def serialize(obj):
        if isinstance(obj, dict):
            items = [f"{CustomSerializer.serialize_key(key)}:{CustomSerializer.serialize(value)}" for key, value in obj.items()]
            return "{" + ";".join(items) + "}"
        elif isinstance(obj, list):
            items = [CustomSerializer.serialize(item) for item in obj]
            return "[" + ",".join(items) + "]"
        elif isinstance(obj, str):
            escaped_str = re.sub(r"([{};:,])", r"\\\1", obj)
            return f"s:{escaped_str}"
        elif isinstance(obj, bool):
            return f"b:{obj}"
        elif isinstance(obj, int):
            return f"i:{obj}"
        elif isinstance(obj, float):
            return f"f:{obj}"
        else:
            raise TypeError(f"Type {type(obj)} not supported for serialization.")

    @staticmethod
    def serialize_key(key):
        return key

    @staticmethod
    def deserialize(serialized_str):
        if serialized_str.startswith("{") and serialized_str.endswith("}"):
            serialized_str = serialized_str[1:-1]
            items = CustomSerializer._split_items(serialized_str, ";")
            obj = {}
            for item in items:
                key, value = CustomSerializer._split_items(item, ":", 1)
                obj[key] = CustomSerializer.deserialize(value)
            return obj
        elif serialized_str.startswith("[") and serialized_str.endswith("]"):
            serialized_str = serialized_str[1:-1]
            items = CustomSerializer._split_items(serialized_str, ",")
            return [CustomSerializer.deserialize(item) for item in items]
        elif serialized_str.startswith("s:"):
            return re.sub(r"\\([{};:,])", r"\1", serialized_str[2:])
        elif serialized_str.startswith("i:"):
            return int(serialized_str[2:])
        elif serialized_str.startswith("f:"):
            return float(serialized_str[2:])
        elif serialized_str.startswith("b:"):
            return serialized_str[2:] == "True"
        else:
            raise ValueError(f"Cannot deserialize string: {serialized_str}")

    @staticmethod
    def _split_items(serialized_str, delimiter, maxsplit=-1):
        result = []
        current = []
        escaped = False
        depth = 0

        for char in serialized_str:
            if escaped:
                current.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char in "{[":
                depth += 1
                current.append(char)
            elif char in "}]":
                depth -= 1
                current.append(char)
            elif char == delimiter and depth == 0:
                result.append("".join(current))
                current = []
            else:
                current.append(char)

        result.append("".join(current))
        if maxsplit != -1:
            return result[:maxsplit] + [delimiter.join(result[maxsplit:])]
        return result

def main():
    original_data = {
        "name": "Mesaerion: The Best Science Fiction Stories 1800-1849",
        "price": 37.59,
        "details": {
            "UPC": "e30f54cea9b38190",
            "availability": "In stock (19 available)",
            "ratings": [5, 4, 3, 4, 5],
            "review_count": 10
        },
        "on_sale": True
    }

    serialized_data = CustomSerializer.serialize(original_data)
    print("Serialized Data:")
    print(serialized_data)

    deserialized_data = CustomSerializer.deserialize(serialized_data)
    print("\nDeserialized Data:")
    print(deserialized_data)

main()
