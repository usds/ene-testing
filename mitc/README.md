# Running a local MAGI in the Cloud

## Step 1: Auth

1. Navigate to https://registry2.omb.gov/
   1. you'll need your PIV
   2. probably easier to do this on your laptop not the virtual box
   3. click on your name in the upper right
   4. select "user profile"
   5. copy the CLI Secret
   6. note the capitalization of your email address: it is important
2. back on the linux virtual machine:
   1. docker login -u *email_address* registry2.omb.gov
   2. supply the CLI secret when prompted for the password

## Step 2: build

`docker build -t registry2.omb.gov:me -f me.dockerfile .`

## Step 3: run

`me_pid=$(docker run -d -p 3000:3000 -t registry2.omb.gov:me)`

## Step 4: profit!

Browse over to [http://127.0.0.1:3000/#/application](http://127.0.0.1:3000/#/application)

## Step 5: clean up

`docker kill $me_pid``