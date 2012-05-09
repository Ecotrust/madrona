.. _appgen_project:

Using the Madrona Virtual Machine 
=========================================================

This tutorial will walk through:

1. Downloading and installing the Madrona virtual machine
2. Creating an initial app using the graphical "Madrona App Generator"
3. Customizing the app

.. note:: You'll need a Windows or OSX system that can run the Google Earth Web Plugin

Downloading and installing the virtual machine
###############################################

First we need to get the Madrona VM up and running on your machine:

1. Download and install `VirtualBox <http://www.virtualbox.org/>`_ for your operating system

2. Download the `Madrona Virtual Machine <https://s3.amazonaws.com/madrona_vm/madrona_virtual_v1.ova>`_ (.ova format; ~ 1GB) 

3. Navigate to File > Import Applicance > and select the madrona_virtual_v1.ova file.

4. Set up networking. In the VM Manager, 

    * select the Madrona VM 
    * click the "Settings" icon
    * click on "Network"
    * check that your network card is listed in the "Name" field
    * click "OK"

5. Start the virtual machine and click "Start Using the Madrona VM"

.. image:: initvm.png

6. Follow the instructions on screen to set up networking 

.. image:: hostsvm.png

.. note:: TODO: Add tutorial link (direct link to the 'Creating the initial demo app' section below) to the Welcome page.

Creating the initial demo app 
###############################

Now that your virtual machine is up and running and your networking is setup, access the app generator from a web browser in your *host* operatings system (not the VM).

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

6. Now let's create some features.  Click the `Public Proposals` tab in the top left

7. Click `Create New` and 
.. note:: TODO: Provide additional information (or a link) covering the tool itself.  I.E. Instructions for signing in, creating an AOI, a Folder, and dragging the AOI into the Folder.  Could also cover Data Layer and Tools panels as well as Export and Edit...


Viewing and editing the generated code
---------------------------------------

Now we'll go back to the Virtual Machine window to see the code that was generated through this process. 

The weird little icon in the lower-left is your "Start" button. From there you can access ``Start > Accessories`` and open:

1. ``LXTerminal`` (a command line terminal)
2. ``File Manager`` (for browsing and editing files)

.. image:: terminal.png

In the LXTerminal window, type::

    cd /usr/local/userapps/testappDemoProject/testappdemoproject

Using the File Manager, navigate to that same directory and go into the ``testapp`` folder. Now you're ready to begin customizing the app.

.. include:: tutorial_customize_appgen.rst
    
