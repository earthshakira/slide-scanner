# Slides App

## How to Run
> Needs Docker

1. Build using docker inside the project directory
```shell
    docker build ./  -t wss-slides 
```
This will create an image with the name `wss-slides`

2. Run the docker image

```shell
    docker run -p8000:8000 -p8765:8765 --name wss-slides wss-slides
```
This will run the image with the name `wss-slides`

3. Go to your browser and visit http://localhost:8000 to see the website

4. To reset the application run
```shell
    docker stop wss-slides
    docker rm wss-slides
```
then run the application again
