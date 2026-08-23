import re

readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove markdown image embeds ![...](...)
cleaned = re.sub(r'!\[.*?\]\(.*?\)\n?', '', content)

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Cleaned README.md: all markdown image tags removed.")
