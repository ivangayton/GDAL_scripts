
wget https://github.com/OSGeo/gdal/releases/download/v3.2.2/gdal-3.2.2.tar.gz
tar -xvf gdal-3.2.2.tar.gz

./ECWJP2SDKSetup_5.5.0.2034.bin

sudo cp -r hexagon/ERDAS-ECW_JPEG_2000_SDK-5.5.0/Desktop_Read-Only/ /usr/local

sudo ln -s /usr/local/Desktop_Read-Only/lib/cpp11abi/x64/release/libNCSEcw.so.5.5.0 /usr/local/lib/libNCSEcw.so.5.5.0


sudo apt install gcc
sudo apt install g++
sudo apt install libproj-dev

cd gdal-3.2.2/

./configure --with-ecw=/usr/local/Desktop_Read-Only
