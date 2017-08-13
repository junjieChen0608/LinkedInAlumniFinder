# Still under development!

# copies python image
FROM python:3.5

# creates src directory within docker container
RUN mkdir -p /usr/src/app

# sets working directory
WORKDIR /usr/src/app

# copies requirements to the src directory
ONBUILD COPY requirements.txt /usr/src/app/

# pip installs requirements
ONBUILD RUN pip3 install --no-cache-dir -r requirements.txt

# copies entire app to docker src directory
ONBUILD COPY . /usr/src/app
