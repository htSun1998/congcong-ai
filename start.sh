kill -9 $(lsof -t -i:3100)

nohup /data/anaconda3/envs/congcong/bin/python /data/projects/congcong-ai/app.py > /dev/null 2>&1 &
