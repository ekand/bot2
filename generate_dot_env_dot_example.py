import os

with open(".env") as f:
    lines = f.read().strip().split("\n")


out_lines = []
for line in lines:
    first_part = line.split("=")[0]
    out_lines.append(first_part + "=" + "changeme")

if os.path.exists("test.env.example"):
    raise ValueError("test.env.example already exists")

with open("test.env.example", "w") as f:
    f.write("\n".join(out_lines))
