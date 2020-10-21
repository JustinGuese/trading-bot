#!/bin/bash
sudo yum install git -y
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/ec2-user/miniconda.sh
cd /home/ec2-user
bash ./miniconda.sh -b -p /home/ec2-user/miniconda
git clone https://github.com/JustinGuese/trading-bot
cd trading-bot/
/home/ec2-user/miniconda/bin/conda init bash
source /home/ec2-user/.bashrc
conda create --name trading -y
source activate trading
conda install pip -y 

# reqs



python train.py data/BTCUSD\=X_1d_all.csv data/BTCUSD\=X_1d_test.csv --model-name btcusd1d_30 --pretrained --episode-count 432
git add -A
git commit -m "training done"
git push origin master
# this will need sudo
shutdown -h now

