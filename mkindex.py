import os
import datetime

files = os.listdir("src/posts")
print(files)

posts = []
for file in files:
    with open(f"src/posts/{file}") as f:
        title = f.readline() # title
        f.readline() # author
        fdate = f.readline()
        date = datetime.datetime.strptime(fdate[2:-1], "%d %B %Y")
        posts.append((file[:-3], title, date.date()))

links = sorted(posts, key=lambda x: x[2], reverse=True)
print(links)

index = f"""% Tidbits
%
%

"""

for link in links:
    index += f" * [{link[1][2:].strip()}](posts/{link[0]}.html)\n"

with open("index.md", "w") as f:
    f.write(index)
