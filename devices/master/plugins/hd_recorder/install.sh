sudo apt install -y webfs curl ffmpeg
sudo sed -ibak 's/web_root="\/var\/www\/html"/web_root="\/var\/schnipsl"/' /etc/webfsd.conf
sudo sed -ibak 's/web_port=""/web_port="9092"/' /etc/webfsd.conf
sudo mkdir /var/schnipsl
sudo chmod a+rw /var/schnipsl
# in /etc/webfsd.conf
#  web_root="/var/schnipsl" 
# setzen
