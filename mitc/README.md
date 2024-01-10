# Running a local MAGI in the Cloud

## Step 1: Auth

First time only:

1. Navigate to https://registry2.omb.gov/
   1. You'll likely need your PIV
   2. Probably easier to do this on your laptop not the virtual box, though if you have a Mac you will need to do it on the virtual box
   3. Click on your name in the upper right
   4. Select "User Profile"
   5. Copy the CLI Secret
   6. Note the capitalization of your email address: it is important
2. Back on the linux virtual machine:
   1. If you didn't login to registry2.omb.gov on your linux VM, make sure you do, or else when you run Docker you'll get a "Bad Gateway" response.
   2. Run `docker login -u <email_address> registry2.omb.gov`
   3. Supply the CLI secret when prompted for the password

## Step 2: build

If the image doesn't exist, or if you have modified it:

`./mitc.sh build`

**TODO**: find out how/if we can share images

## Step 3: run

`./mitc.sh start`

## Step 4: profit!

Browse over to [http://127.0.0.1:3000/#/application](http://127.0.0.1:3000/#/application)

## Step 5: clean up

`./mitc.sh stop`
