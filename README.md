📘 COOKBOOK
📄 Overview
This project loads recipe information from a JSON file and stores it in a structured SQLite database.
It is designed to help process large recipe datasets and convert them into a clean, queryable format.

🎯 Features
•	Loads JSON recipe data (single object or list of recipes)
•	Validates the JSON file before processing
•	Creates a new SQLite database automatically
•	Builds a structured recipe table
•	Inserts every recipe into the database
•	Handles unexpected or missing fields safely
•	Includes a viewer utility to inspect the database contents

📁 Project Components
•	JSON Loader — Reads and validates the JSON input
•	Database Creator — Builds a new SQLite database
•	Table Generator — Creates a standardized recipe table
•	Insert Engine — Adds recipes into the database one by one
•	Database Viewer — Allows you to check stored recipes

🔄 Workflow
1.	A JSON file containing recipe data is supplied.
2.	The program loads and validates the file.
3.	A new SQLite database is created.
4.	The recipe table is generated if it doesn’t already exist.
5.	Each recipe from the JSON file is inserted into the table.
6.	A viewer script can be run to inspect the stored data.

🗂 Database Structure
The database stores recipe details including:
•	Cuisine
•	Title
•	Rating
•	Preparation, cooking, and total time
•	Description
•	Nutritional information
•	Serving size
The nutritional information is saved in JSON format inside the database so it can preserve structure.

🧪 Error Handling
The system checks for:
•	Missing or invalid JSON files
•	Incorrect JSON formats
•	Database connection issues
•	Insertion errors for individual recipes
Clear messages are displayed for each error, ensuring transparency and easier debugging.

📊 Viewing the Data
The project includes a tool for exploring database contents. This allows you to see:
•	Available tables
•	Inserted recipe entries
•	Fields stored for each recipe
🧩 Requirements
No external dependencies are required.
The project uses only standard Python libraries, which makes it easy to run on any system.

🚀 Future Enhancements
Possible improvements include:
•	A REST API for serving recipe data
•	A React-based user interface
•	Search and filtering capabilities
•	Better normalization of nutritional details
•	Import/export options

