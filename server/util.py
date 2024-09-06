import pickle
import json
import numpy as np
import os

# Global variables to hold loaded artifacts
__locations = None
__data_columns = None
__model = None

def get_estimated_price(location, sqft, bhk, bath):
    """Estimate the price of the home based on location, sqft, bhk, and bath."""
    try:
        # Get the index of the location in the data columns
        loc_index = __data_columns.index(location.lower())
    except ValueError:
        return "Invalid location"  # Handle location not found in data

    # Create a numpy array to hold the input features
    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    
    if loc_index >= 0:
        x[loc_index] = 1  # Set the location-specific feature

    # Return the predicted price, rounded to 2 decimal places
    return round(__model.predict([x])[0], 2)

def load_saved_artifacts():
    """Load the model and column information from the saved artifacts."""
    print("Loading saved artifacts...start")
    global __data_columns
    global __locations
    global __model

    # Retrieve paths from environment variables or use local paths
    base_dir = os.path.dirname(__file__)
    columns_path = os.path.join(base_dir, 'artifacts', 'columns.json')
    model_path = os.path.join(base_dir, 'artifacts', 'banglore_home_prices_model.pickle')

    # Load the data columns (features and locations) from local file
    try:
        with open(columns_path, 'r') as f:
            columns_data = json.load(f)
            __data_columns = columns_data['data_columns']
            __locations = __data_columns[3:]  # First 3 columns are sqft, bath, bhk
    except FileNotFoundError:
        print(f"Error: The columns file {columns_path} was not found.")
        raise
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {columns_path}.")
        raise

    # Load the trained model from local file
    try:
        with open(model_path, 'rb') as f:
            __model = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: The model file {model_path} was not found.")
        raise
    except pickle.PickleError:
        print(f"Error: Failed to load the model from the file {model_path}.")
        raise

    print("Loading saved artifacts...done")

def get_location_names():
    """Return a list of location names."""
    return __locations

def get_data_columns():
    """Return a list of all data columns (including sqft, bath, bhk, and locations)."""
    return __data_columns

if __name__ == '__main__':
    # Test the functions when running this script directly
    load_saved_artifacts()
    print(get_location_names())
    print(get_estimated_price('1st Phase JP Nagar', 1000, 3, 3))
    print(get_estimated_price('1st Phase JP Nagar', 1000, 2, 2))
    print(get_estimated_price('Kalhalli', 1000, 2, 2))  # Invalid location
    print(get_estimated_price('Ejipura', 1000, 2, 2))
