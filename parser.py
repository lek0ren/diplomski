import re

inpupFile = open("zadaci/textZadatka.txt", "r")



for line in inpupFile:
    print(line)
    matched = re.search(r'for (?P<iterVar>\w+):=(?P<iterVal>\d+) to (?P<endVar>\w+) do',line)
    if matched is not None:
        print(f"for({matched.group('iterVar')} = {matched.group('iterVal')}; {matched.group('iterVar')} < {matched.group('endVar')}; {matched.group('iterVar')}++)")
        