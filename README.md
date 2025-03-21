# Phone Number Tracker

This Python application tracks phone number details including location, carrier, and time zone information. It uses the `phonenumbers` library for phone number parsing and validation, the `opencage` library for geocoding, and `folium` for generating maps. The application also provides a user-friendly graphical interface using `tkinter` and stores tracking logs in a SQLite database.

## Features

* **Phone Number Tracking:** Retrieves country, carrier, time zone, and validation details for a given phone number.
* **Geocoding:** Uses the OpenCage Geocoding API to find the latitude and longitude of the phone number's location.
* **Map Generation:** Generates an HTML map using `folium` to visualize the phone number's location.
* **Database Storage:** Stores tracking logs in a SQLite database (`phone_tracker.db`).
* **Log Management:** Provides functionality to view, search, export to CSV, and clear tracking logs.
* **User Interface:** A graphical user interface (GUI) built with `tkinter` for easy interaction.

## Prerequisites

* Python 3.x
* Libraries: `phonenumbers`, `tkinter`, `sqlite3`, `pandas`, `folium`, `opencage`
    * Install required libraries using pip:
        ```bash
        pip install phonenumbers tkinter pandas folium opencage
        ```
* **OpenCage API Key:** You need an API key from OpenCage Geocoding to use the geocoding feature. Sign up at [OpenCage Geocoding](https://opencagedata.com/) to get your API key.

## How to Run

1.  **Save the Script:** Save the provided Python code as a `.py` file (e.g., `phone_tracker.py`).
2.  **Run the Script:** Open your terminal or command prompt, navigate to the directory where you saved the file, and run the script using the command: `python phone_tracker.py`
3.  **Use the GUI:**
    * Enter the phone number and your OpenCage API key in the respective fields.
    * Click "Track Number" to get the phone number details and location.
    * Click "View All Logs" to display all tracking logs in the table.
    * Click "Export to CSV" to save the logs to a CSV file.
    * Click "Clear Logs" to delete all logs from the database.
    * Use the search bar to search for specific phone numbers.
    * Click "Generate Map" to open an HTML map of the location in your default browser.

## Code Explanation

* **`PhoneNumberTracker` Class:**
    * Initializes the database and GUI.
    * `setup_database()`: Creates the SQLite database and table.
    * `get_local_info()`: Parses the phone number, retrieves details, and geocodes the location.
    * `save_to_database()`: Saves tracking results to the database.
    * `generate_map()`: Generates and opens an HTML map using `folium`.
    * `search_number()`: Searches for a specific phone number in the database.
    * `view_logs()`: Retrieves and displays all logs.
    * `export_to_csv()`: Exports logs to a CSV file.
    * `clear_logs()`: Clears all logs from the database.
    * `update_table()`: Updates the table with new data.
    * `setup_gui()`: Sets up the GUI using `tkinter`.
    * `run()`: Starts the application.
* **Dependencies:**
    * `phonenumbers`: For phone number parsing and validation.
    * `opencage`: For geocoding.
    * `folium`: For generating maps.
    * `tkinter`: For the GUI.
    * `sqlite3`: For database operations.
    * `pandas`: For exporting data to CSV.
    * `webbrowser` : for opening the generated map.
    * `os` : for opening the directory of the exported CSV file.

## Database

* The application uses a SQLite database named `phone_tracker.db` to store tracking logs.
* The database contains a table named `phone_logs` with columns for phone number details and location.

## Notes

* Ensure you have a valid OpenCage API key to use the geocoding and map generation features.
* The application requires an internet connection to retrieve location data.
* The API key is stored in memory during the execution of the program. For more secure applications, use a more secure method of storing and retrieving API keys.
