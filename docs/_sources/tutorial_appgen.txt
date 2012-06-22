.. _appgen_project:

Madrona Appliance Tutorial 
=========================================================

.. note:: We assume you've already `downloaded and installed the Madrona Appliance <http://madrona.ecotrust.org/developer/appliance/>`_ and have a virtual machine (VM) up and running.

This tutorial will walk through:

* Creating an app using the Madrona App Generator
* Getting started customizing the app

1. In your running VM, click "Start Using the Madrona VM"

.. image:: initvm.png

2. The App Generator is now running.  Follow the instructions onscreen to configure your host system to send web requests for 'madrona' to the VM's IP address.

.. note:: this IP address could be different every time you start the VM and you will need to change it.

.. image:: hostsvm.png

Creating the initial demo app 
###############################

Now that your networking is setup, access the app generator from a web browser in your *host* operatings system (not the VM).

.. note:: Why access it from your host system?  The demo uses the Google Earth Web Plugin which isn't available currently for Linux.

1. Open the URL ``http://madrona/``

2. Sign in. The username and password is `madrona` / `madrona`.

3. Click ``Generate New Madrona App`` to begin.

4. Provide the App with a name, we'll be using "Test App" throughout this tutorial.

5. Enter the description ``Test Application`` or whatever you want.

6. Draw a study region on the map.  The studyregion is used to define the geographical extent of your project.  For best results, draw a smaller region.

7. Under `Features`, select the `AOI` feature.  

.. note:: Features are spatial entities that the user will be able to draw, edit and share with other people.

8. (Optionally) create one or more additional features by clicking the '+' button.  Give them a name and a type (point, line, polygon or folder).or create your own by clicking the '+' button.  Once you create more you need to select them all in the `Features` list by holding down the Ctrl key and selecting them all. 

9.  Select one or more of the available KML data layers to make available to your user.

10. (Optionally)  Click the "+" button to add your own KML file if you know the URL.

11. Click ``Save``.  You should now see a summary of your app.

.. image:: appgen_new_or.png

Initialize and Activate Your App
---------------------------------------

1. Click ``Initialize`` This can take up to a minute.  Be patient...

.. note:: Under the hood this is generating the code for your app using some simple commands.  To see what the actual commands look like click the `toggle code` link.

2. Once initialization is complete you will see an ``Activate`` button.  Click the ``Activate`` button.

.. note:: Under the hood this is configuring the Apache web server to make your app available on port 81.  You can only have one app active at one time.

.. image:: appgen_or.png

Test Out Your New App
---------------------------------------

1. In the admin, click ``Go To App``.  This will take you to ``http://madrona:81/``.  When the app loads it will automatically zoom the map to the study region that you drew.  

.. note:: Loading may take a little while the first time as it caches your requests in order to speed up subsequent loads.  If you don't already have the Google Earth Web Plugin installed you will be asked to at this time.  Once you do, refresh the page

2. Click ``Login`` in the top right.  The username and password is `madrona` / `madrona`

3. Click the `Data Layers` icon in the top left.  

.. note:: This is next to the `Tools` icon which looks like a gear. 

4. You should see a `Test App` folder which has a data layer for your study region.  Try turning this on and off.  Double-click to zoom into it.

5. You should also see a `Base KML Data` folder which has all of the data layers that you added.  Try turning them on and off.

6. Now let's create some features.  Click the `My Shapes` tab in the top left.  If you don't see this tab you probably aren't logged in.

7. Click `Create` and then click `AOI` which generically stands for `Area of Interest`.  

8. Click `Draw Shape` and then draw a polygon on the map.  Double-click the last point to finish.

.. note:: Madrona will now validate your shape, make sure you didn't draw any bowties or any other type of self-intersecting polygon.  If it's valid you now have the option of editing your shape or if you are happy click `Next`.

9. Give your new feature a name, any name.  Optionally, give it a description.

10. Click `Submit`

11. You'll now be presented with detailed information for your shape.  Close this window by clicking the 'X'.

12. You should now see your feature in the `Features and Collections`

13. Now let's create a new folder.  Do it the same way you created an AOI, through the `Create` menu.

14. Click and drag your feature you created into your new folder.  You can organize your features any way you like.

.. note:: There are many more things you can do with these features and folders out of the box including edit, delete, copy, share and download.  Try selecting one or more features or folders and performing these actions, for example download an entire folder of features as KML.

Viewing and editing the generated code
---------------------------------------

Now we'll go back to the Virtual Machine window to see the code that was generated through this process. 

1. The icon in the lower-left is your "Start" button.  Yes it looks a little strange. Click ``Start > Accessories > LXTerminal`` to open a command line terminal window

2. Click ``Start > Accessories > Sublime Editor 2``.  This will be your text editor

3. In Sublime Text click ``File > Open Folder`` and then open ``/usr/local/userapps/testDemoProject/testdemoproject``

.. image:: terminal.png

Now you're ready to begin customizing the app.

.. include:: tutorial_customize_appgen.rst
    
