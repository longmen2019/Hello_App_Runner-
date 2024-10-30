import py_avataaars  # Import the py_avataaars library for generating avatar images
import random, logging, sys  # Import standard libraries for random number generation, logging, and system-specific parameters
import uvicorn  # Import uvicorn for running the ASGI server

from starlette.applications import Starlette  # Import Starlette application class
from starlette.routing import Route, Mount  # Import routing classes for defining routes and mounting applications
from starlette.templating import Jinja2Templates  # Import Jinja2Templates for rendering templates
from starlette.config import Config  # Import Config for configuration management
from starlette.staticfiles import StaticFiles  # Import StaticFiles for serving static files
from starlette.responses import PlainTextResponse, JSONResponse  # Import response classes for plain text and JSON responses
from starlette_exporter import PrometheusMiddleware, handle_metrics  # Import Prometheus middleware and metrics handler for monitoring

from json import loads, dumps  # Import JSON functions for loading and dumping JSON data
from requests import get  # Import get function from requests library for making HTTP requests
from os import getenv, urandom, path, environ  # Import OS functions for environment variables, random bytes, and file path operations
from PIL import Image  # Import Image class from PIL (Pillow) for image processing

templates = Jinja2Templates(directory='templates')  # Initialize Jinja2Templates with the directory for templates

global_state = {
    "INITIALIZED": False  # Define a global state dictionary to track initialization status
}

logging.basicConfig(stream=sys.stdout, level=eval('logging.' + getenv('LOG_LEVEL', 'INFO')))  # Configure logging to output to stdout with a level from environment variable
logging.debug('Log level is set to DEBUG.')  # Log a debug message indicating the log level

# Generate and save a local avatar image
def generate_avatar_image():
    logging.info('Generating avatar image')  # Log an info message indicating avatar generation
    custom_circle_colors = [
        'BLUE_01', 'BLUE_02', 'PASTEL_BLUE', 'PASTEL_GREEN', 'PASTEL_ORANGE', 'PASTEL_RED', 'PASTEL_YELLOW',
    ]  # Define a list of custom circle colors
    custom_mouth_types = [
        'DEFAULT', 'EATING', 'GRIMACE', 'SMILE', 'TONGUE', 'TWINKLE',
    ]  # Define a list of custom mouth types
    custom_eyebrow_types = [
        'DEFAULT', 'DEFAULT_NATURAL', 'FLAT_NATURAL', 'RAISED_EXCITED', 'RAISED_EXCITED_NATURAL', 'SAD_CONCERNED', 'SAD_CONCERNED_NATURAL', 'UNI_BROW_NATURAL', 'UP_DOWN', 'UP_DOWN_NATURAL', 'FROWN_NATURAL',
    ]  # Define a list of custom eyebrow types
    custom_eye_types = [
        'DEFAULT', 'CLOSE', 'EYE_ROLL', 'HAPPY', 'HEARTS', 'SIDE', 'SQUINT', 'SURPRISED', 'WINK', 'WINK_WACKY',
    ]  # Define a list of custom eye types

    # pick a random value from default types
    def r(enum_):
        return random.choice(list(enum_))  # Return a random choice from the given enumeration

    # Make a random customization selection from custom arrays
    def rc(customization, array):
        return eval("py_avataaars." + customization + "." +  random.choice(array))  # Return a random choice from the given customization array

    avatar = py_avataaars.PyAvataaar(
        style=py_avataaars.AvatarStyle.CIRCLE,  # Set avatar style to CIRCLE
        background_color=rc("Color", custom_circle_colors),  # Set background color to a random choice from custom circle colors
        skin_color=r(py_avataaars.SkinColor),  # Set skin color to a random choice from SkinColor enumeration
        hair_color=r(py_avataaars.HairColor),  # Set hair color to a random choice from HairColor enumeration
        facial_hair_type=r(py_avataaars.FacialHairType),  # Set facial hair type to a random choice from FacialHairType enumeration
        facial_hair_color=r(py_avataaars.HairColor),  # Set facial hair color to a random choice from HairColor enumeration
        top_type=r(py_avataaars.TopType),  # Set top type to a random choice from TopType enumeration
        hat_color=r(py_avataaars.Color),  # Set hat color to a random choice from Color enumeration
        mouth_type=rc("MouthType", custom_mouth_types),  # Set mouth type to a random choice from custom mouth types
        eye_type=rc("EyesType", custom_eye_types),  # Set eye type to a random choice from custom eye types
        eyebrow_type=rc("EyebrowType", custom_eyebrow_types),  # Set eyebrow type to a random choice from custom eyebrow types
        nose_type=r(py_avataaars.NoseType),  # Set nose type to a random choice from NoseType enumeration
        accessories_type=r(py_avataaars.AccessoriesType),  # Set accessories type to a random choice from AccessoriesType enumeration
        clothe_type=r(py_avataaars.ClotheType),  # Set clothe type to a random choice from ClotheType enumeration
        clothe_color=r(py_avataaars.Color),  # Set clothe color to a random choice from Color enumeration
        clothe_graphic_type=r(py_avataaars.ClotheGraphicType),  # Set clothe graphic type to a random choice from ClotheGraphicType enumeration
    )

    try:
        avatar.render_png_file('avatar.png')  # Render the avatar and save it as 'avatar.png'
    except Exception as e:
        logging.ERROR('Could not write avatar file with error: %s', e)  # Log an error message if the avatar file could not be written

# Generate and save a social media banner image
def generate_social_card(avatar_file):
    logging.info('Generating social card image.')  # Log an info message indicating social card generation
    # We have two backgrounds to choose from
    base_image_options = ['banner_base_light.png', 'banner_base_dark.png']  # Define a list of base image options
    base_image = random.choice(base_image_options)  # Choose a random base image

    # open our images to use them
    background = Image.open(base_image)  # Open the chosen base image
    foreground = Image.open(avatar_file)  # Open the avatar image file

    # resize the image to 439x439 (default image size is 280x280)
    resized_foreground = foreground.resize((439, 439))  # Resize the avatar image to 439x439 pixels

    # placement values for avatar on top of background
    background_width_center = int(background.width * .0258 )  # Calculate the x-coordinate for placing the avatar
    background_height_center = int(background.height * .145)  # Calculate the y-coordinate for placing the avatar
    # paste the avatar on top of the background in the right location
    background.paste(resized_foreground, (background_width_center,background_height_center), resized_foreground)  # Paste the resized avatar onto the background
    # save the new image
    try:
        background.save('./static/social.png')  # Save the combined image as 'social.png'
    except Exception as e:
        logging.ERROR('Could not save twitter banner with error: %s', e)  # Log an error message if the social card could not be saved

def homepage(request):
    return PlainTextResponse('Hello, world!')  # Return a plain text response with 'Hello, world!'

def _setup(request):
    random.seed(str(request.url))  # Seed the random number generator with the request URL
    if not path.isfile('avatar.png'):
        generate_avatar_image()  # Generate an avatar image if it does not exist
    if not path.isfile('./static/social.png'):
        generate_social_card('avatar.png')  # Generate a social card if it does not exist
    global_state["INITIALIZED"] = True  # Set the global state to initialized

def index(request):
    if "Go-http-client" in request.headers['user-agent']:
        # Filter out health checks from the load balancer
        return PlainTextResponse("healthy")  # Return a plain text response indicating health
    if "curl" in request.headers['user-agent']:
        return templates.TemplateResponse('index.txt', {'request': request})  # Return a template response for curl requests
    else:
        if not global_state["INITIALIZED"]:
            _setup(request)  # Set up the application if not initialized
        return templates.TemplateResponse('index.html', {'request': request})  # Return a template response for other requests

def headers(request):
    return JSONResponse(dumps({k:v for k, v in request.headers.items()}))  # Return a JSON response with request headers

routes = [
    Route('/', endpoint=index),  # Define a route for the index endpoint
    Route('/headers', endpoint=headers),  # Define a route for the headers endpoint
    Mount('/static', app=StaticFiles(directory='static'), name='static'),  # Mount the static files directory
]

app = Starlette(debug=True, routes=routes)  # Create a Starlette application with debug mode and defined routes
app.add_middleware(PrometheusMiddleware)  #