# Quickstart Example

> Downloading public domain books and converting Romeo and Juliet to molds:

```
git@github.com:Braillest/webapp.git
cd webapp
./scripts/copy-env.bash
docker compose up -d
docker exec -it braillest_core_backend bash
python3 ./python/download_books.py
cp "/data/source-material/texts/Romeo and Juliet by William Shakespeare (1840).txt" /data/texts/Romeo-and-Juliet.txt
python3 ./python/generate_all_page_molds.py /data/texts/Romeo-and-Juliet.txt
```
