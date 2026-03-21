from enum import Enum
from typing import cast
from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection
from datetime import datetime, date

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
    MILEAGE = "CurrentMileage"
    BRANCH_ID = "BranchId"

# enum for storing all valid VehicleTypes
class VehicleType(Enum):
    SEDAN = "Sedan"
    TRUCK = "Truck"
    SUV = "SUV"
    VAN = "Van"

class TableName(Enum):
    VEHICLE_TYPE = "VehicleType"
    RENTAL_BRANCH = "RentalBranch"
    MAINTENANCE_STAFF = "MaintenanceStaff"
    VEHICLE = "Vehicle"
    CUSTOMER = "Customer"
    RENTAL_AGREEMENT = "RentalAgreement"
    MAINTENANCE_RECORD = "MaintenanceRecord"

class RentalAgreementStatus(Enum):
    BOOKED = "Booked"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"