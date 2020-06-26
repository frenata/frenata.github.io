import os
import datetime

files = os.listdir("src/posts")

posts = []
for file in files:
    with open(f"src/posts/{file}") as f:
        title = f.readline() # title
        f.readline() # author
        fdate = f.readline()
        date = datetime.datetime.strptime(fdate[2:-1], "%d %B %Y")
        posts.append((file[:-3], title, date.date()))

links = sorted(posts, key=lambda x: x[2], reverse=True)

index = f"""% Tidbits
%
% {datetime.date.today().strftime("%d %B %Y")}

"""

for link in links:
    index += f" * [{link[1][2:].strip()}](posts/{link[0]}.html) - {link[2]}\n"

with open("index.md", "w") as f:
    f.write(index)
