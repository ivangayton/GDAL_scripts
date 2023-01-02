# Install GRASS extensions within QGIS

Within a standard QGIS installation on Linux, you have the GRASS tools included. Just go to `processing -> toolbox` and voila, there they are.

However, there are a lot of GRASS plugins that don't come bundled withe the default installation of GRASS within QGIS. To get them, you have to install them from the [GRASS GIS Addons repository](https://grass.osgeo.org/grass78/manuals/addons/). This is a pain.

To install from this repository, first go to `plugins -> Manage and Install Plugins` and search for `GRASS`. Check to activate. The GRASS window should pop open automatically, but greyed out; you can't do fuck-all with it yet.

You need to create a mapset. Why? I don't know. Whatever. Just do it. Go to `Plugins -> GRASS -> New mapset`. Choose a directory for GRASS's database, give it a project name, pick an extent (which might as well be the extent of the project you're currently working on, I don't know if that makes a difference or not), and hit the create button. Yay, things are now un-greyed-out.

In the GRASS Modules, you now have one called the GRASS Shell. Click it and you'll get a console. Type `g.extension -l` and you'll get a list of the extensions available for install in the Addons repository. Scroll up to see if the one you want is in there. If not, I don't know what to tell you.

Now try to install it with `g.extension extension=<extension_name>`. For example, I want the image cutlines extension, so I type `g.extension extension=i.cutlines`.

Of course, this probably won't actually work. It'll try to fetch the relevant plugin from the repository, but you'll as likely as not get an error like: `svn: E170000: URL 'https://github.com/OSGeo/grass-addons/trunk/grass7/imagery/i.cutlines' doesn't exist`. Cool huh? Aren't you glad you chose Free Software instead of paying a predatory monopolist like ESRI?

Fuckin' A. Let's carry on here. [This page](https://grass.osgeo.org/grass78/manuals/g.extension.html) purports to describe the `g.extension` command, which should help us figure out how to get this yak shaved nice and smooth.

Turns out you can specify a URL. So let's try (using my example of the cutlines extension) `g.extension extension=i.cutlines url="https://github.com/OSGeo/grass-addons/tree/grass7/src/imagery/i.cutlines"`

That also fails. The manual suggests you can specify the git branch, which causes the console to complain that `branch` is an invalid parameter. Awesome!

Ok, so clone the entire Git repo locally, and try the installation from a local directory: `g.extension extension=i.cutlines url="/home/ivan/Documents/git/grass-addons/src/imagery/i.cutlines"`.

That results in a happy message: `GRASS_INFO_MESSAGE(111235,1): Installation of <i.cutlines> successfully finished GRASS_INFO_END(111235,1)`.

Followed by a sad message: `GRASS_INFO_WARNING(111236,1): This add-on module will not function until you set the GRASS_ADDON_BASE environment variable (see "g.manual variables") GRASS_INFO_END(111236,1)`.

WTAF?

Ok, let's dig into that error. Stack Exchange suggests `g.gisenv set="GRASS_ADDON_BASE=~/.grass7/addons"`. That doesn't obviously do anything (the console simply performs a carriage return). However, if you do it, and _then_ run the install command again, it might work. It did, for me, once.

Good luck!

