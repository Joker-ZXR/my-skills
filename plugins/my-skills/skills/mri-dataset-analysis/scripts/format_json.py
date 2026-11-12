#!/usr/bin/env python3
"""Format JSON objects with indentation and every array on one line."""
import argparse
import json
from pathlib import Path
from validate_metadata import reject_constant, unique_object


def format_value(value, level=0):
    if isinstance(value, dict) and value:
        indent = '  ' * (level + 1)
        items = [indent + json.dumps(key, ensure_ascii=False) + ': ' + format_value(item, level + 1)
                 for key, item in value.items()]
        return '{\n' + ',\n'.join(items) + '\n' + '  ' * level + '}'
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(', ', ': '))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    for path in args.files:
        data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
        result = format_value(data) + '\n'
        assert json.loads(result) == data
        path.write_text(result, encoding='utf-8')
        print(f'Formatted: {path}')


if __name__ == '__main__':
    main()
