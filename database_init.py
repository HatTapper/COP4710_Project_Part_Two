import mysql.connector
from mysql.connector.cursor import MySQLCursor
from typing import cast
from definitions import VehicleType

# iterates through the database and verifies that every
# necessary table and column exists
# note that this does not verify the types of the columns and their constraints,
# or if the primary keys are configured correctly
def verifyDatabaseIntegrity(cursor: MySQLCursor):
    isValid = True
    reason = ""

    def tableExists(tableName: str):
        cursor.execute("SHOW TABLES LIKE %s", (tableName,))
        return cursor.fetchone() is not None

    def columnExists(tableName: str, columnName: str):
        cursor.execute(f"SHOW COLUMNS FROM `{tableName}` LIKE %s", (columnName,))
        return cursor.fetchone() is not None
    
    # iterates through table with given column names and returns
    # True if the column exists, else False and a string containing
    # the missing column name within the table
    def iterateColumnNames(tableName: str, columnNames: list[str]):
        isValid = True
        reason = ""

        for columnName in columnNames:
         if not columnExists(tableName, columnName):
            isValid = False
            reason = f"Table with name `Vehicle` is lacking column with name `{columnName}`"
            break
        
        return isValid, reason

    vehicleColumnNames = [
        "VehicleID", "LicensePlate",
        "Make", "Model",
        "Year", "Color",
        "DailyRate", "CurrentMileage",
        "isAvailable", "VehicleTypeID",
        "BranchID",
    ]
    vehicleTypeColumnNames = [
        "VehicleTypeID", "TypeName",
    ]
    rentalBranchColumnNames = [
        "BranchID", "BranchName",
        "Address", "Phone",
    ]
    maintenanceStaffColumnNames = [
        "StaffID", "FirstName",
        "LastName", "OfficeNumber",
        "Phone", "Email",
        "BranchID",
    ]
    customerColumnNames = [
        "CustomerID", "FirstName",
        "LastName", "Address",
        "Phone", "Email",
        "DriverLicenseNumber", "LicenseExpiryDate",
    ]
    rentalAgreementColumnNames = [
        "AgreementID", "CustomerID",
        "VehicleID", "PickupBranchID",
        "ReturnBranchID", "ScheduledPickup",
        "ScheduledReturn", "ActualPickup",
        "ActualReturn", "EstimatedCost",
        "ActualCost", "Status",
    ]
    maintenanceRecordColumnNames = [
        "RecordID", "VehicleID",
        "CustomerID", "StaffID",
        "IssueType", "IssueDescription",
        "IssueStatus", "DateReported",
        "TimeReported", "DateTimeResolved",
        "Notes",
    ]

    tableColumnDict = {
        "Vehicle": vehicleColumnNames,
        "VehicleType": vehicleTypeColumnNames,
        "RentalBranch": rentalBranchColumnNames,
        "MaintenanceStaff": maintenanceStaffColumnNames,
        "Customer": customerColumnNames,
        "RentalAgreement": rentalAgreementColumnNames,
        "MaintenanceRecord": maintenanceRecordColumnNames,
    }

    for tableName, columnNames in tableColumnDict.items():
        isValidTable = tableExists(tableName)
        if not isValidTable:
            isValid = False
            reason = f"Table under name {tableName} does not exist"
            break

        isValid, reason = iterateColumnNames(tableName, columnNames)
        if not isValid:
            break
    
    
    return isValid, reason

def sanitizeVehicleTypeTable(cursor: MySQLCursor):
    missing = []

    for vehicle in VehicleType:
        cursor.execute("SELECT * FROM VehicleType WHERE TypeName = %s", (vehicle.value,))
        if cursor.fetchone() is None:
            missing.append((vehicle.value,))

    if len(missing) > 0:
        print(f"Appended missing VehicleType items: {missing}")
        cursor.executemany("INSERT INTO VehicleType (TypeName) VALUES (%s)", missing)

    return len(missing) > 0


# helper function to connect to the provided database, ensuring its integrity
# before returning the cursor to the caller
def connectToDatabase(hostName: str, userName: str, userPass: str, dbName: str):
    db = mysql.connector.connect(
        host=hostName,
        user=userName,
        password=userPass,
        database=dbName,
    )
    # fixing type checker issues
    cursor = cast(MySQLCursor, db.cursor())

    isValid, reason = verifyDatabaseIntegrity(cursor)

    if not isValid:
        raise RuntimeError(f"Database under name {dbName} did not pass integrity check. Reason supplied: {reason}")
    
    dbChanged = sanitizeVehicleTypeTable(cursor)
    if dbChanged:
        db.commit()
    
    return db, cursor

