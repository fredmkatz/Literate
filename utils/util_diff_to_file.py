import difflib

def diff_to_file(path1, path2, diffpath, **diff_options):
    with open(path1, 'r',encoding="utf-8") as file1, open(path2, 'r',encoding="utf-8") as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()

    diff = difflib.unified_diff(file1_lines, file2_lines, lineterm="")
    difflines = []
    for line in diff:
        if line.startswith(("+", "-")):
            difflines.append(line)
      #      print(line)


    with open(diffpath, 'w',encoding="utf-8") as diff_file:
        diff_file.writelines(difflines)

# Example usage:
# diff_to_file('file1.txt', 'file2.txt', 'diff.txt')