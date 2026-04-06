# Profile_Launcher_Firefox_Addon
A simple Firefox addon that lets you open new instances of differents profiles easier, even from others browsers

![screen1](Screenshots/Screenshot1.png) ![screen2](Screenshots/Screenshot2.png) ![screen3](Screenshots/Screenshot3.png) ![screen4](Screenshots/Screenshot4.png)

Addon Link: https://addons.mozilla.org/en-US/firefox/addon/profile-launcher/

This addon connects to a python script through Firefox native-messaging since addons cant directly interact with the profiles.

<br>IMPORTANT<br>
Due to this limitation you must have python installed on your system, if using windows remember to check the Add to Path checkbox during the python instalation.<br>
Besides having the addon you must run the pl_installer on this repo and that will set up the native-messaging and everything else necesary.

<br>NOTICE<br>
On Windows firefox cant open graphical applications from the addons, so when clicking the profile it will open a folder with a bat file inside and you must open that in order to open the new browser instance.

Due to this limitation the Create, Rename and Delete functions are linux only.
