
wget https://github.com/OSGeo/gdal/releases/download/v3.2.2/gdal-3.2.2.tar.gz
tar -xvf gdal-3.2.2.tar.gz

unzip ECWJP2SDKSetup_5.5.0.2034-Update3-Linux.zip
sudo chmod +x ECWJP2SDKSetup_5.5.0.2034.bin 
./ECWJP2SDKSetup_5.5.0.2034.bin

## Choose 1, desktop read-only, and spacebar to the end and type yes
## to pretend to accept the T&Cs

sudo cp -r hexagon/ERDAS-ECW_JPEG_2000_SDK-5.5.0/Desktop_Read-Only/ /usr/local

sudo ln -s /usr/local/Desktop_Read-Only/lib/cpp11abi/x64/release/libNCSEcw.so.5.5.0 /usr/local/lib/libNCSEcw.so.5.5.0


sudo apt install build-essential
sudo apt install g++
sudo apt install libproj-dev

cd gdal-3.2.2/

./configure --with-ecw=/usr/local/Desktop_Read-Only

make

sudo make install

# Set variables

echo 'export LD_LIBRARY_PATH=/usr/local/lib' >> ~/.profile

echo 'export LD_LIBRARY_PATH=/usr/local/lib' >> ~/.bashrc

GDAL_DATA="/usr/local/share/gdal"

ldconfig

# Check if ECW is installed

gdalinfo -formats | grep ECW
