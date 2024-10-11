import re


class CustomSerializer:
    @staticmethod
    def serialize(obj):
        """Converts a Python object (dict, list, str, int, float, bool) into a custom serialized string."""
        if isinstance(obj, dict):
            items = [f"{CustomSerializer.serialize_key(key)}:{CustomSerializer.serialize(value)}" for key, value in
                     obj.items()]
            return "{" + ";".join(items) + "}"
        elif isinstance(obj, list):
            items = [CustomSerializer.serialize(item) for item in obj]
            return "[" + ",".join(items) + "]"
        elif isinstance(obj, str):
            # Escape special characters like colon, semicolon, etc.
            escaped_str = re.sub(r"([{};:,])", r"\\\1", obj)
            return f"s:{escaped_str}"
        elif isinstance(obj, bool):
            return f"b:{obj}"  # Correctly serialize booleans as b:True or b:False
        elif isinstance(obj, int):
            return f"i:{obj}"
        elif isinstance(obj, float):
            return f"f:{obj}"
        else:
            raise TypeError(f"Type {type(obj)} not supported for serialization.")

    @staticmethod
    def serialize_key(key):
        """Serializes dictionary keys as plain strings without any prefixes."""
        # Keys are always serialized as plain strings
        return key

    @staticmethod
    def deserialize(serialized_str):
        """Converts a custom serialized string back into its original Python object."""
        if serialized_str.startswith("{") and serialized_str.endswith("}"):
            # Deserialize a dictionary
            serialized_str = serialized_str[1:-1]  # Remove the outer {}
            items = CustomSerializer._split_items(serialized_str, ";")
            obj = {}
            for item in items:
                key, value = CustomSerializer._split_items(item, ":", 1)
                obj[key] = CustomSerializer.deserialize(value)  # Keys are plain strings, so no deserialization needed
            return obj
        elif serialized_str.startswith("[") and serialized_str.endswith("]"):
            # Deserialize a list
            serialized_str = serialized_str[1:-1]  # Remove the outer []
            items = CustomSerializer._split_items(serialized_str, ",")
            return [CustomSerializer.deserialize(item) for item in items]
        elif serialized_str.startswith("s:"):
            # Deserialize a string
            return re.sub(r"\\([{};:,])", r"\1", serialized_str[2:])  # Unescape special characters
        elif serialized_str.startswith("i:"):
            # Deserialize an integer
            return int(serialized_str[2:])
        elif serialized_str.startswith("f:"):
            # Deserialize a float
            return float(serialized_str[2:])
        elif serialized_str.startswith("b:"):
            # Deserialize a boolean
            return serialized_str[2:] == "True"
        else:
            raise ValueError(f"Cannot deserialize string: {serialized_str}")

    @staticmethod
    def _split_items(serialized_str, delimiter, maxsplit=-1):
        """Splits a string on the given delimiter, respecting nested structures and escaped characters."""
        result = []
        current = []
        escaped = False
        depth = 0  # Tracks the depth of nested structures (brackets {})

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


# Example usage
def main():
    # A complex object containing dict, list, str, int, float, and bool
    original_data = {
        "name": "Mesaerion: The Best Science Fiction Stories 1800-1849",
        "price": 37.59,
        "details": {
            "UPC": "e30f54cea9b38190",
            "availability": "In stock (19 available)",
            "ratings": [5, 4, 3, 4, 5],
            "review_count": 10
        },
        "on_sale": True  # Boolean value, correctly serialized as b:True
    }

    # Serialize the data
    serialized_data = CustomSerializer.serialize(original_data)
    print("Serialized Data:")
    print(serialized_data)

    # Deserialize the data back to original form
    deserialized_data = CustomSerializer.deserialize(serialized_data)
    print("\nDeserialized Data:")
    print(deserialized_data)


# Run the example
main()
