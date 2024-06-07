import fnmatch
import os


def read_ignore_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Add force ignore project assets and system directories
    # @eaDir is Synology system's own folder, ignore it
    lines += ['.git', '.ignore', '.gitignore', 'venv/', '.venv/', '.env', '@eaDir']
    rules = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return rules


def is_ignored(file, rules):
    for rule in rules:
        if fnmatch.fnmatch(file, rule):
            return True
        # Check if the rule is a directory pattern
        if rule.endswith('/'):
            # Check if the file path starts with the directory pattern
            if fnmatch.fnmatch(file, rule + '*'):
                return True
    # Special case for '@ear' directories
    if '@eaDir/' in file or file.startswith('@eaDir/'):
        return True
    return False


class FileEntryIter:
    def __init__(self, input_path):
        self.is_folder = os.path.isdir(input_path)
        if self.is_folder:
            rule_file = os.path.join(input_path, '.ignore')
        else:
            folder, _ = os.path.split(input_path)
            rule_file = os.path.join(folder, '.ignore')
        self.rules = read_ignore_file(rule_file) if os.path.exists(rule_file) else []
        self.path = input_path
        self.iterator = os.scandir(self.path) if self.is_folder else iter([os.DirEntry(input_path)])

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                entry = next(self.iterator)
                if is_ignored(entry.path, self.rules):
                    continue
                return entry
            except StopIteration:
                raise


def read_rules_relative(path):
    is_folder = os.path.isdir(path)
    if is_folder:
        rule_file = os.path.join(path, '.ignore')
    else:
        folder, _ = os.path.split(path)
        rule_file = os.path.join(folder, '.ignore')
    return read_ignore_file(rule_file) if os.path.exists(rule_file) else []


def travel_folder(path, handler, rules=None, travel_end=True):
    if not path:
        raise ValueError('path is empty')
    if not os.path.exists(path):
        raise ValueError('path does not exist')

    if rules is None:
        rules = []

    relative_rules = read_rules_relative(path)
    under_rules = rules + relative_rules

    if os.path.isfile(path):
        if not is_ignored(os.path.basename(path), under_rules):
            handler(path)
    elif os.path.isdir(path):
        for entry in FileEntryIter(path):
            if is_ignored(entry.path[len(path) + 1:], under_rules):  # Use relative path for matching
                continue
            if entry.is_dir() and travel_end:
                travel_folder(entry.path, handler, under_rules, travel_end)
            handler(entry.path)


# def travel_folder(path, handler, rules, travel_end=True):
#     if not path:
#         raise ValueError('path is empty')
#     if not os.path.exists(path):
#         raise ValueError('path is not exist')
#
#     relative_rules = read_rules_relative(path)
#     under_rules = [*rules, *relative_rules]
#
#     if os.path.isfile(path):
#         if is_ignored(path, under_rules):
#             pass
#         else:
#             handler(path)
#             return
#     elif os.path.isdir(path):
#         for entry in FileEntryIter(path):
#             if is_ignored(entry.path, under_rules):
#                 continue
#             if entry.is_dir() and travel_end:
#                 travel_folder(entry.path, handler, under_rules, True)
#                 handler(entry.path)
#             else:
#                 # is file entry
#                 handler(entry.path)


class OSUTIL:
    """
    extension of file
    """

    def __init__(self):
        pass
