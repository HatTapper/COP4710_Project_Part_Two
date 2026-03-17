from enum import Enum

# enum is used for handling vehicle input fields
# and acts as a key for labeling each input field
# when received by methods
class VehicleInputField(Enum):
    LICENSE_PLATE = "LicensePlate"
    NAME = "Name"
    MAKE = "Make"
    YEAR = "Year"
    MODEL = "Model"
    COLOR = "Color"
    DAILY_RATE = "DailyRate"
    MILEAGE = "Mileage"

# enum for storing all valid VehicleTypes
class VehicleType(Enum):
    SEDAN = "Sedan"
    TRUCK = "Truck"
    SUV = "SUV"
    VAN = "Van"