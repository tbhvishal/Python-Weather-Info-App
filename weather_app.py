import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import threading
import time
import config  # Import the configuration file

# Function to fetch and display weather information based on the city
def get_weather(city_name=config.DEFAULT_CITY):
    # Show a loading message while fetching data
    info_label.config(text="Loading", font=("Arial", 14, "bold"), fg="#000000")
    app.update()  # Refresh the window to show the "Loading" text

    time.sleep(3)  # Simulate a delay of 3 seconds to represent fetching data

    try:
        # Make the API request to fetch weather details for the given city
        complete_url = f"{config.BASE_URL}q={city_name}&appid={config.API_KEY}&units=metric"
        response = requests.get(complete_url)
        data = response.json()

        # Check if the city is found in the API response
        if data.get("cod") != 404:
            # Extracting weather data
            main = data.get("main", {})
            wind = data.get("wind", {})
            weather_desc = data["weather"][0]["description"] if data["weather"] else "N/A"
            temp = main.get("temp", "N/A")
            pressure = main.get("pressure", "N/A")
            humidity = main.get("humidity", "N/A")
            wind_speed = wind.get("speed", "N/A")
            city = data.get("name", "N/A")
            country = data["sys"].get("country", "N/A")
            sunrise = datetime.fromtimestamp(data["sys"].get("sunrise", 0)).strftime('%H:%M:%S')
            sunset = datetime.fromtimestamp(data["sys"].get("sunset", 0)).strftime('%H:%M:%S')

            # Update the city input field with the searched city
            city_entry.delete(0, tk.END)  # Clear the current text in the entry box
            city_entry.insert(0, city)  # Insert the new city name that the user searched for

            # Show the fetched weather data in the info label
            info_label.config(
                text=f"City: {city}, {country}\nTemperature: {temp}°C\n"
                     f"Weather: {weather_desc.capitalize()}\n"
                     f"Pressure: {pressure} hPa\nHumidity: {humidity}%\n"
                     f"Wind Speed: {wind_speed} m/s\nSunrise: {sunrise}\nSunset: {sunset}",
                font=("Arial", 12), fg=config.INFO_TEXT_COLOR  # Set the font and color for the weather info text
            )

            # Reset the search button after fetching the data
            search_button.config(state="normal", text="Search", image=search_icon, compound="left")
        else:
            # Show error message if the city is not found
            info_label.config(text="Not Found. Please provide a valid city name.", fg="#000000", font=("Arial", 12, "bold"))
            search_button.config(state="normal", text="Search", image=search_icon, compound="left")
    except Exception as e:
        # Display error message if there's an issue fetching data
        info_label.config(text="Provide a valid city name to get info", fg="#000000", font=("Arial", 12, "bold"))
        search_button.config(state="normal", text="Search", image=search_icon, compound="left")

# Function to handle the search action when the user clicks the "Search" button
def search_city():
    city_name = city_entry.get()  # Get the city name entered by the user
    if city_name:
        search_button.config(state="disabled", text="Searching", image=None, fg="#FFFFFF")  # Disable button and show "Searching"
        threading.Thread(target=get_weather, args=(city_name,)).start()  # Start a new thread to fetch weather data
    else:
        # Show a message to prompt the user to enter a city name
        info_label.config(text="Enter city name to get weather info", fg="#000000", font=("Arial", 12, "bold"))

# Function to bind the Enter key to the search function
def on_enter_press(event):
    search_city()  # Call search_city function when Enter key is pressed

# Function to handle resizing of the background image when the window is resized
def resize_bg(event):
    new_bg = bg_image.resize((event.width, event.height), Image.LANCZOS)  # Resize the background image
    bg_photo = ImageTk.PhotoImage(new_bg)  # Convert the resized image into a format suitable for Tkinter
    bg_label.config(image=bg_photo)  # Update the background label with the new image
    bg_label.image = bg_photo  # Keep a reference to the image

# Function to set the background image (path is passed as argument)
def set_background(image_path):
    try:
        global bg_image  # Declare bg_image as global so it can be accessed in resize_bg
        bg_image = Image.open(image_path)  # Open the background image
        bg_photo = ImageTk.PhotoImage(bg_image.resize((500, 400), Image.LANCZOS))  # Resize it to fit the window
        bg_label.config(image=bg_photo)  # Set the background image in the label
        bg_label.image = bg_photo  # Store the reference to the background image
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")  # Show an error message if the file is not found

# Function to show the default weather info for the default city
def show_default_info():
    get_weather(config.DEFAULT_CITY)  # Fetch and display weather info for the default city

# GUI setup
app = tk.Tk()  # Create the main window
app.title("Weather Info")  # Set the window title
app.geometry("500x400")  # Set the window size
app.iconbitmap("assets/weather.ico") # Set the window icon

# Set up the background label (initialize it here)
bg_label = tk.Label(app)
bg_label.place(relwidth=1, relheight=1)  # Fill the entire window with background image

# Set a customizable background image (default to background.png)
set_background(config.DEFAULT_BACKGROUND_IMAGE)

# Heading label with drop shadow (No background)
title_label = tk.Label(app, text="☂ Weather Info ☂", font=("Arial", config.HEADER_TOP_TEXT_SIZE, "bold"),
                       fg=config.HEADER_TOP_TEXT_COLOR, relief="solid", bd=config.HEADER_TEXT_TOP_BORDER_THICKNESS, padx=10, pady=5)
title_label.place(relx=0.5, rely=0.06, anchor="n")  # Centered at the top of the window

# City input field with custom border color
city_entry = tk.Entry(app, font=("Arial", 14), width=30, bd=2, relief="solid", 
                      highlightbackground=config.SEARCH_BAR_BORDER_COLOR,
                      highlightcolor=config.SEARCH_BAR_BORDER_COLOR,
                      justify="center")  # Center align the text in the search box
city_entry.place(relx=0.5, rely=0.2, anchor="n")  # Centered below the title label
city_entry.insert(0, "Enter city name here")  # Set the placeholder text
city_entry.bind("<Return>", on_enter_press)  # Bind Enter key to the search function

# Search button with a custom icon
search_icon = ImageTk.PhotoImage(Image.open(config.SEARCH_ICON_IMAGE).resize((20, 20)))  # Load the search icon
search_button = tk.Button(app, text="Search", command=search_city, font=("Arial", 12, "bold"), image=search_icon,
                          compound="left", bg=config.SEARCH_BUTTON_COLOR, fg=config.SEARCH_BUTTON_TEXT_COLOR, padx=10)
search_button.place(relx=0.5, rely=0.3, anchor="n")  # Centered below the city entry box

# Info box for displaying weather details with black text and border
info_label = tk.Label(app, text="Weather info will appear here", font=("Arial", 12), fg=config.INFO_TEXT_COLOR, relief="solid", bd=config.INFO_BORDER_THICKNESS)
info_label.place(relx=0.5, rely=0.43, anchor="n", width=370)  # Centered below the search button

# Footer with credit info
footer_label = tk.Label(app, text="Code With ♥ By Vishal Sharma", font=("Arial", 10, "italic"), fg="#000000", anchor="center")
footer_label.place(x=0, y=375, relwidth=1, height=25)  # Footer at the bottom of the window

# Show default info when the app starts
show_default_info()  # Display weather info for the default city when the app loads

app.mainloop()  # Run the main event loop to keep the window open
