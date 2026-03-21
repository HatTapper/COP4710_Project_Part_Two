import mysql.connector
from definitions import *

# performs a MySQL query given the cursor and query details without risk of unhandled exception
# will return the error thrown by the cursor if an issue with the query occurs
def performSafeQuery(cursor: MySQLCursor, query: str, params=None):
    try:
        cursor.execute(query, params)
        return None
    except Exception as e:
        return e
    
cachedVehicleTypeIds: dict[str, int] = {}
    
def getVehicleTypeId(cursor: MySQLCursor, vehicleType: str):
    if cachedVehicleTypeIds.get(vehicleType):
        return cachedVehicleTypeIds[vehicleType]
    
    query = "SELECT VehicleTypeID FROM VehicleType WHERE TypeName = %s"
    params = (vehicleType,)
    error = performSafeQuery(cursor, query, params)
    
    if error:
        print(error)
        return -1
    
    result = cursor.fetchone()
    # we know from the table structure that the ID will either be an int or
    # return None if it does not exist
    result = cast(tuple[int] | None, result)

    if result is not None:
        cachedVehicleTypeIds[vehicleType] = result[0]
        return result[0]
    
    return -1
    
def initializeTestingData(database: MySQLConnection, cursor: MySQLCursor):
    def customerExists(licenseNumber: str):
        query = "SELECT * FROM Customer WHERE DriverLicenseNumber = %s"
        params = (licenseNumber,)
        error = performSafeQuery(cursor, query, params)
        return (error is not None) or (cursor.fetchone() is not None)
    
    def getCustomerId(licenseNumber: str):
        query = "SELECT CustomerID FROM Customer WHERE DriverLicenseNumber = %s"
        params = (licenseNumber,)
        error = performSafeQuery(cursor, query, params)
        if error is None:
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            return -1
        return -1
    
    def vehicleExists(licensePlate: str):
        query = "SELECT * FROM Vehicle WHERE LicensePlate = %s"
        params = (licensePlate,)
        error = performSafeQuery(cursor, query, params)
        return (error is not None) or (cursor.fetchone() is not None)
    
    def getVehicleId(licensePlate: str):
        query = "SELECT VehicleID FROM Vehicle WHERE LicensePlate = %s"
        params = (licensePlate,)
        error = performSafeQuery(cursor, query, params)
        if error is None:
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            return -1
        return -1
    
    def branchExists(branchName: str):
        query = "SELECT * FROM RentalBranch WHERE BranchName = %s"
        params = (branchName,)
        error = performSafeQuery(cursor, query, params)
        return (error is not None) or (cursor.fetchone() is not None)
    
    def agreementExists(pickupTime: datetime):
        query = "SELECT * FROM RentalAgreement WHERE ScheduledPickup = %s"
        params = (pickupTime,)
        error = performSafeQuery(cursor, query, params)
        return (error is not None) or (cursor.fetchone() is not None)
    
    JOHN_DOE_LICENSE_NUM = "123456789"
    JANE_DOE_LICENSE_NUM = "987654321"
    HONDA_CIVIC_PLATE = "901243"

    if not customerExists(JOHN_DOE_LICENSE_NUM):
        query = """
                INSERT INTO Customer (FirstName, LastName, Address, Phone, Email, DriverLicenseNumber, LicenseExpiryDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        params = ("John", "Doe", "65th St.", "252-124-3532", "john.doe@gmail.com", JOHN_DOE_LICENSE_NUM, date(2027, 12, 25),)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return
        
    if not customerExists(JANE_DOE_LICENSE_NUM):
        query = """
                INSERT INTO Customer (FirstName, LastName, Address, Phone, Email, DriverLicenseNumber, LicenseExpiryDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        params = ("Jane", "Doe", "65th St.", "252-565-3342", "jane.doe@gmail.com", JANE_DOE_LICENSE_NUM, date(2027, 12, 25),)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return
    
    if not branchExists("Central VRMS Branch"):
        query = """
            INSERT INTO RentalBranch (BranchName, Address, Phone)
            VALUES (%s, %s, %s)
        """
        params = ("Central VRMS Branch", "128th Ave.", "732-242-2545",)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return
    
    query = """
        SELECT BranchID FROM RentalBranch WHERE BranchName = %s
    """
    params = ("Central VRMS Branch",)
    error = performSafeQuery(cursor, query, params)
    
    if error:
        print(f"Initialization with test values failed. Last recorded error: {error}")
        return
    
    firstBranchId = cursor.fetchone()
    if firstBranchId is None:
        print("For some reason, the branch did not load with a branch ID, maybe database error?")
        return
    firstBranchId = cast(int, firstBranchId[0])

    if not branchExists("Sub VRMS Branch"):
        query = """
            INSERT INTO RentalBranch (BranchName, Address, Phone)
            VALUES (%s, %s, %s)
        """
        params = ("Sub VRMS Branch", "128th Ave.", "732-242-2545",)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return
    
    query = """
        SELECT BranchID FROM RentalBranch WHERE BranchName = %s
    """
    params = ("Sub VRMS Branch",)
    error = performSafeQuery(cursor, query, params)
    
    if error:
        print(f"Initialization with test values failed. Last recorded error: {error}")
        return
    
    secondBranchId = cursor.fetchone()
    if secondBranchId is None:
        print("For some reason, the branch did not load with a branch ID, maybe database error?")
        return
    secondBranchId = cast(int, secondBranchId[0])

        
    if not vehicleExists(HONDA_CIVIC_PLATE):
        query = """
            INSERT INTO Vehicle (LicensePlate, Make, Model, Color, DailyRate, Year, CurrentMileage, BranchID, VehicleTypeID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (HONDA_CIVIC_PLATE, "Honda", "Civic", "Red", "32.95", "2026", "40000", firstBranchId, getVehicleTypeId(cursor, VehicleType.SEDAN.value),)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return
    
    if not agreementExists(datetime(2026, 4, 16)):
        query = """
            INSERT INTO RentalAgreement (CustomerID, VehicleID, PickupBranchID, ReturnBranchID, ScheduledPickup, ScheduledReturn, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (getCustomerId(JOHN_DOE_LICENSE_NUM), getVehicleId(HONDA_CIVIC_PLATE), firstBranchId, secondBranchId, datetime(2026, 4, 16), datetime(2026, 4, 20), RentalAgreementStatus.BOOKED.value,)
        error = performSafeQuery(cursor, query, params)

        if error:
            print(f"Initialization with test values failed. Last recorded error: {error}")
            database.rollback()
            return

    print("Initialization with test values succeeded")
    database.commit()


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
    
    if not tableExists(TableName.VEHICLE_TYPE.value):
        print("Client does not have VehicleType table, creating...")
        query = """
            CREATE TABLE VehicleType(
	            VehicleTypeID INT PRIMARY KEY AUTO_INCREMENT,
	            TypeName VARCHAR(50) NOT NULL UNIQUE
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing VehicleType table : {error}"
            return isValid, reason

    if not tableExists(TableName.RENTAL_BRANCH.value):
        print("Client does not have RentalBranch table, creating...")
        query = """
            CREATE TABLE RentalBranch(
                BranchID 	INT PRIMARY  KEY AUTO_INCREMENT,
                BranchName  VARCHAR(50)  NOT NULL,
                Address 	VARCHAR(200) NOT NULL,
                Phone 		VARCHAR(20)  NOT NULL
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing RentalBranch table : {error}"
            return isValid, reason

    if not tableExists(TableName.MAINTENANCE_STAFF.value):
        print("Client does not have MaintenanceStaff table, creating...")
        query = """
            CREATE TABLE MaintenanceStaff(
                StaffID        INT  PRIMARY KEY  AUTO_INCREMENT,
                FirstName      VARCHAR(50)   NOT NULL,
                LastName       VARCHAR(50)   NOT NULL,
                OfficeNumber   VARCHAR(50)   NOT NULL,
                Phone          VARCHAR(20)   NOT NULL,
                Email          VARCHAR(50)   NOT NULL UNIQUE,
                BranchID 	   INT  NOT NULL,
                
                FOREIGN KEY (BranchID) REFERENCES RentalBranch(BranchID)
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing MaintenanceStaff table : {error}"
            return isValid, reason

    if not tableExists(TableName.VEHICLE.value):
        print("Client does not have Vehicle table, creating...")
        query = """
            CREATE TABLE Vehicle(
                VehicleID 	   INT 			  PRIMARY KEY AUTO_INCREMENT,
                LicensePlate   VARCHAR(20)    NOT NULL UNIQUE,
                Make 		   VARCHAR(50)    NOT NULL,
                Model 		   VARCHAR(50)    NOT NULL,
                Year 		   SMALLINT 	  NOT NULL,
                Color 		   VARCHAR(30)    NOT NULL,
                DailyRate      DECIMAL(8, 2)  NOT NULL,
                CurrentMileage INT UNSIGNED  NOT NULL,
                IsAvailable    BOOLEAN 		  NOT NULL DEFAULT TRUE,
                VehicleTypeID  INT 			  NOT NULL,
                BranchID 	   INT 			  NOT NULL,

                CHECK (Year > 1900),
                
                FOREIGN KEY(VehicleTypeID) REFERENCES VehicleType(VehicleTypeID),
                FOREIGN KEY (BranchID) 	   REFERENCES RentalBranch(BranchID)
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing Vehicle table : {error}"
            return isValid, reason

    if not tableExists(TableName.CUSTOMER.value):
        print("Client does not have Customer table, creating...")
        query = """
            CREATE TABLE Customer(
                CustomerID 			INT 		 PRIMARY KEY AUTO_INCREMENT,
                FirstName 			VARCHAR(50)  NOT NULL,
                LastName 			VARCHAR(50)  NOT NULL,
                Address 			VARCHAR(200) NOT NULL,
                Phone 				VARCHAR(20)  NOT NULL,
                Email 				VARCHAR(100) NOT NULL UNIQUE,
                DriverLicenseNumber VARCHAR(50)  NOT NULL UNIQUE,
                LicenseExpiryDate   DATE 		 NOT NULL
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing Customer table : {error}"
            return isValid, reason
        
    if not tableExists(TableName.RENTAL_AGREEMENT.value):
        print("Client does not have RentalAgreement table, creating...")
        query = """
            CREATE TABLE RentalAgreement(
                AgreementID		INT PRIMARY KEY AUTO_INCREMENT,
                CustomerID		INT NOT NULL,
                VehicleID		INT NOT NULL,
                PickupBranchID  INT NOT NULL,
                ReturnBranchID  INT NOT NULL,
                ScheduledPickup	DATETIME NOT NULL,
                ScheduledReturn DATETIME NOT NULL,
                ActualPickup	DATETIME,
                ActualReturn	DATETIME,
                EstimatedCost	DECIMAL(10, 2),
                ActualCost		DECIMAL(10, 2),
                Status		VARCHAR(20) NOT NULL,
                
                CHECK(Status IN('Booked', 'Active', 'Completed', 'Cancelled')),
                CHECK(ScheduledReturn > ScheduledPickup),
                
                FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID),
                FOREIGN KEY(VehicleID) REFERENCES Vehicle(VehicleID),
                FOREIGN KEY(PickupBranchID) REFERENCES RentalBranch(BranchID),
                FOREIGN KEY(ReturnBranchID) REFERENCES RentalBranch(BranchID)
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing RentalAgreement table : {error}"
            return isValid, reason
        
    if not tableExists(TableName.MAINTENANCE_RECORD.value):
        print("Client does not have MaintenanceRecord table, creating...")
        query = """
            CREATE TABLE MaintenanceRecord (
                RecordID INT PRIMARY KEY AUTO_INCREMENT,
                VehicleID INT NOT NULL,
                CustomerID INT,
                StaffID INT,
                IssueType VARCHAR(20) NOT NULL,
                IssueDescription TEXT NOT NULL,
                IssueStatus VARCHAR(20) NOT NULL,
                DateReported DATE NOT NULL,
                TimeReported TIME NOT NULL,
                DateTimeResolved DATETIME,
                Notes TEXT,
                
                CHECK (IssueType IN ('Routine' , 'Urgent')),
                CHECK (IssueStatus IN ('Reported' , 'In-Progress', 'Complete', 'Awaiting Parts')),
                
                FOREIGN KEY (VehicleID) REFERENCES Vehicle (VehicleID),
                FOREIGN KEY (CustomerID) REFERENCES Customer (CustomerID),
                FOREIGN KEY (StaffID) REFERENCES MaintenanceStaff (StaffID)
            );
        """
        params = None
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            isValid = False
            reason = f"Error initalizing MaintenanceRecord table : {error}"
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

