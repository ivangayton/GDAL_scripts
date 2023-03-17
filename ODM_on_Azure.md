# OpenDroneMap on Azure Cloud

## Set up the Azure cloud machine
- Get an Azure account, with a sponsor, permission to create resources, etc. Figure out how to log into the management portal.
- Go to `Home`, and select `Create a resource`. Find `Ubuntu Server 22.04 LTS` (probably other versions of Ubuntu would work, but this is what I used) and press the `Create` link.
- Presumably you have a Subscription and Resource Group selectable on your Azure account. Pick them. If your permissions are configured correctly, you will now have the ability to create resources. Suggested settings:
  - Fill out Virtual Machine Name with whatever you want.
  - Pick a Region, either close to your users' location, or---if you have other resources like storage already in the Azure cloud---in the same region as your other stuff.
  - The Image I'm using is Ubuntu Server 22.04 LTS - x64 Gen2. It seems fine.
  - VM architecture is x64.
  - The size is pretty critical; ODM is pretty memory-intensive, and jobs may crash after running out of memory if you don't have enough. On the other hand, setting up a server with more than you need wastes money. I'm using the tier `Standard_E32-8ds_v5 - 8 vcpus, 256 GiB memory`. That costs about $2.50 an hour, which adds up really fast (about $1,700 a month).
  - Username; I usually change it from `azureuser` to something less pathetic and easier to type, like `hot`. It doesn't really matter.
  - You'll probably want to generate a new key pair. Give it a memorable unique name. Whatever you do, _don't lose it_!. When you download the key pair, you'll want to put it somewhere safe (I use `~/.ssh`  and lock down the file permissions on it (so that ssh won't complain); for example `sudo chmod 400 ~/.ssh/hot-odm-key.pem`. If you've already got keys up on Azure, you can select `Stored Keys` and use those instead (at your own risk; if you don't have the corresponding private key you won't be able to access anything).
  - Under `Allow selected ports` you'll want to enable all of the ports in the dropdown: 80, 443, and 22. It'll flash a warning at you explaining that this will allow all IP addresses to access your virtual machine, which is true insofar as you've allowed others to have access to the SSH private key from the preceding step (in other words, if you haven't done anything dumb it's not true so don't worry about it).
- Now to the next page, Disks.
  - Don't bother with `Encryption at host` unless you feel the need.
  - The default `OS disk type` is fine.
  - **Do** select `Delete with VM`! If you don't, you're liable to have an expensive hard drive sitting there racking up charges after you think you've deleted your ODM machine! Of course, try not to delete the machine until you've backed up all the data on it...
  - You probably don't need `Key management`, unless (again) you feel the need for data security (I'm assuming here that you want this machine to process more or less publicly-accessible OpenDroneMap data, not Personally Identifiable Information or your banking info). `Enable Ultra Disk compatibitility` is also not necessary under the circumstances. 
  - Hit the `Create and attach a new disk` link. Most of the defaults (`Name`, which will be something vaguely related to the name of the machine you gave earlier, `Source type`, which will be empty disk, `Size`, which will be 1024 GiB, `Key Management`, which will be Platform-managed key, and `Enable shared disk`, which will be "No", are all fine. **However, `Delete disk with VM` must be checked** for the same reason we mentioned earlier; you don't want the disk sitting there racking up charges after you're done with the ODM processing! When you press `Ok`, you'll see the disk configuration at the bottom of the screen. I think you probably want to set `Host caching` to "Read/write" (though I'm not certain this refers to regular access, maybe it's just for memory caching, in which case it probably doesn't matter).
- On to the next page: Networking.
  - The defaults are probably fine, though if you're setting up multiple resources you might want to put them all in the same `Virtual network`.
  - You'll probably see the warning about all IP addresses being able to access your machine again, and again this can be ignored if you've been careful with the SSH key.
- On to the Management page.
  - Oh, look! A bunch of Microsoft-related stuff I don't understand. Probably safe to ignore. Backups seem like a good idea, but they actually probably aren't worth it for this use-case; for the most part raw photos go onto the machine, processed ODM products come off of it, and that's the end of it. No need for persistent backup.
- On to Monitoring.
  - Defaults.
- On to Advanced.
  - Don't think we need any of that stuff.
- On to Tags.
  - I guess your accounting department might be interested in this?
- On to Review + create
  - You can check all of the selections you made here, and have a look a the estimated pricing, and if you're comfortable with that, hit the `Create` button!

If all goes well, soon you'll have a running cloud machine.

## Access the machine, configure it, and set up WebODM

### SSH in and do some housekeeping
- Go to the Azure portal `Home`, click on `Virtual machines`, and click on the machine you just created (whose name you presumably remember). Look for the "Public IP address".
- Point a domain name at the IP address (yeah, I know, that's easier said than done but there are lots of tutorials on the Web).
- With the IP address, you can probably ssh into the machine like so: `ssh -i ~/.ssh/hot-kakuma-odm-2.pem hot@my.odm.domain`. The `hot` in this case is the username I chose instead of `azureuser`, and the domain is the one I pointed at the instance (though while I wait for DNS to propagate I'm more likely using the raw IP address, like so: `ssh -i ~/.ssh/hot-kakuma-odm-2.pem hot@20.123.12.134` or whatever the IP address is.
- Once you're in, do some housekeeping.
```
sudo apt update
sudo apt upgrade -y
sudo apt install -y emacs-nox
sudo apt install -y python3-pip

sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/ap

sudo apt update
sudo apt install -y docker-ce
sudo apt install -y docker-compose
sudo usermod -aG docker ${USER}
```

### Format, partition, and mount the data drive
- Use `lsblk` to list the drives. The one that has no children (i.e. /dev/sda or /dev/sdc but no /dev/sda1 or /dev/sdcw1 beneath it) is the one we'll be working with.
- Format the disk with `sudo parted /dev/sda mklabel gpt`
- Now create a partition with `sudo parted -a opt /dev/sda mkpart primary ext4 0% 100%`. Once this is done, `lsblk` should reveal a partition named something like `/dev/sdc1` or `/dev/sda1`.
- Create an ext4 filesystem on the disk with `sudo mkfs.ext4 -L data /dev/sda1` (or whatever your disk is if not sda1).
- Get the UUID of the new partition with `lsblk -fs`. It'll be something snappy like 99aa0ac6-3a91-4842-9d26-2bce55a55dc2 Copy it.
- Create a mount path with something like `sudo mkdir /home/hot/odm-data`
- Update your filesystem table (fstab) with `sudo emacs /etc/fstab`. Add the line `UUID=99aa0ac6-3a91-4842-9d26-2bce55a55dc2 /home/hot/odm-data ext4 defaults 0 2` (with the correct UUID, and mount path.
- Reboot with `sudo reboot now`. Hold your breath. After you let your breath out again, SSH back in. When you're back in, `df -h` should show you a drive with lots of free space at the mount point you specified.

## Configure Docker to use that big drive instead of filling up your OS drive and crashing your server.
__NOTE: This is *not* the correct way to do this. The correct way would---I think---be instructing WebODM to use specific volumes. But this works (I've cribbed it from the method I use when setting up ODK Central servers) by fooling Docker into putting its entire being into a directory symlinked to a drive other than the OS disk.__

```
mkdir /home/hot/odm-data/docker
sudo echo '{ "data-root": "/home/hot/odm-data/docker" }' | sudo tee -a /etc/docker/daemon.json
sudo service docker stop
sudo rsync -aP /var/lib/docker/ /home/hot/odm-data/docker/
sudo mv /var/lib/docker /var/lib/docker.old
sudo reboot now
```

### Clone the WebODM repo and fire that puppy up

```
git clone https://github.com/OpenDroneMap/WebODM --config core.autocrlf=input --depth 1

cd WebODM

./webodm.sh start
```

Stop it with `ctrl-c`. Now use `screen` to execute
```
./webodm.sh restart --ssl --hostname my.url.com
```






  
  
  