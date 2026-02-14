# Count the keys in the JSON data in the Epstein files.
import re
from collections import defaultdict

from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.util.helpers.data_helpers import sort_dict
from epstein_files.output.rich import highlighter, print_subtitle_panel

INDENT = '  '
GUID_REGEX = re.compile(r'[-\d\w]{36}')


class JsonStats:
    key_count = defaultdict(int)
    list_count = 0

    def count_obj(self, obj: object, height: int = 0):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'bannerType' and v == 'any':
                    continue

                self.count_obj(v, height + 1)

                if not GUID_REGEX.match(k):
                    self.key_count[k] += 1

                if isinstance(v, str) and self.is_interesting_key(k):
                    if k != 'URL' or not v.startswith('asset:'):
                        key_value = Text(INDENT * height).append(k, style='cyan').append(': ').append(f'"{v}"')
                        console.print(highlighter(key_value))
        elif isinstance(obj, list):
            self.list_count += 1

            for item in obj:
                self.count_obj(item, height + 1)

    def is_interesting_key(self, key: str) -> bool:
        if 'Color' in key or 'Alignment' in key:
            return False
        elif key.startswith("text") and key != 'text':
            return False
        elif key.startswith('font') or key.startswith('ignore') or 'color' in key.lower() or key.startswith('thumbnail'):
            return False
        elif key in ['bottom', 'classification', 'fillMode', 'identifier', 'layout', 'role', 'style', 'top', 'type', 'weightLabel', 'width']:
            return False
        elif key.lower().endswith('height') or key.endswith('Identifier'):
            return False
        elif not self.should_count(key):
            return False

        return True

    def should_count(self, key: str) -> bool:
        if GUID_REGEX.match(key):
            return False
        elif key.startswith('call-to-action') or key.startswith('icon'):
            return False
        elif key in ['familyName']:
            return False

        return True


stats = JsonStats()

for json_file in epstein_files.json_files:
    stats.count_obj(json_file.json_data())

console.line(4)
print_subtitle_panel("Counts of Keys in JSON data")

for (key, count) in sort_dict(stats.key_count):
    console.print(f"{key}: {count}")

console.print(f"\n\nFound {stats.list_count} lists.\n")
