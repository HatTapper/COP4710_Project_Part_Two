import flet as ft
from database_connection import connectToDatabase, performSafeQuery, initializeTestingData, getVehicleTypeId
from definitions import *

# replace parameters with your data
DB_HOST_NAME = "localhost"
DB_USER_NAME = "root"
DB_USER_PASS = "6432"
DB_DATABASE_NAME = "vrms"

# if the database should be initialized with testing data
# to assist in program functionality
# this inserts customers, vehicles, branches, and rental agreements
INITIALIZE_TESTING_DATA = True

database, cursor = connectToDatabase(
    hostName=DB_HOST_NAME,
    userName=DB_USER_NAME,
    userPass=DB_USER_PASS,
    dbName=DB_DATABASE_NAME,
)

if INITIALIZE_TESTING_DATA:
    initializeTestingData(cast(MySQLConnection, database), cursor)

# this is run by flet at startup, treat as a standard main function
def main(page: ft.Page):
    SCREEN_WIDTH = page.window.width
    SCREEN_HEIGHT = page.window.height

    if SCREEN_WIDTH is None or SCREEN_HEIGHT is None:
        return
    
    HALF_SCREEN_WIDTH = SCREEN_WIDTH / 2

    vehicleInputColumn = prepareVehicleInputFields(SCREEN_WIDTH)
    customerAgreementColumn = prepareCustomerAgreementViewer(SCREEN_WIDTH)

    insertCarContainer = ft.Container(
        width=HALF_SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        bgcolor=ft.Colors.WHITE,
        alignment=ft.Alignment.CENTER,
        expand=True,
        content=vehicleInputColumn,
        padding=ft.Padding.symmetric(vertical=20, horizontal=30),
    )

    viewAgreementsContainer = ft.Container(
        width=HALF_SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        bgcolor=ft.Colors.WHITE,
        alignment=ft.Alignment.CENTER,
        expand=True,
        content=customerAgreementColumn,
        padding=ft.Padding.symmetric(vertical=20, horizontal=30),
    )

    dividerLine = ft.Container(
        width=10,
        height=SCREEN_HEIGHT,
        bgcolor=ft.Colors.BLACK,
    )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    layout = ft.Row(
        controls=[
            insertCarContainer, dividerLine, viewAgreementsContainer
        ],
        spacing=0,
        expand=True
    )

    page.add(layout)



def getEstimatedCost(startTime: datetime, endTime: datetime, dailyRate: float):
    timeDelta = endTime - startTime
    secondsToDays = timeDelta.total_seconds() / 86400

    return secondsToDays * dailyRate

# called when the button to submit Vehicle table data is pressed, requires the dict of input fields that
# fulfill the table data and the dropdown
def onVehicleInputSubmit(inputFields: dict[VehicleInputField, ft.TextField], vehicleTypeDropdown: ft.Dropdown, resultText: ft.Text):
    def isValidInput(inputName: VehicleInputField, inputValue: str):
        if inputValue.strip() == "":
            field = inputFields.get(inputName)
            if field:
                field.error = "This field is required"
                
            return False
        
        if inputName == VehicleInputField.YEAR:
            inputtedYear = None
            try:
                inputtedYear = int(inputValue)
            except ValueError:
                return False
            
            if inputtedYear < 1900:
                field = inputFields.get(inputName)
                if field:
                    field.error = "Year is too low"

                return False
        elif inputName == VehicleInputField.DAILY_RATE:
            inputtedRate = None
            try:
                inputtedRate = float(inputValue)
            except ValueError:
                return False
            
            # checks if the user put in a leading decimal point
            if inputtedRate < 1:
                field = inputFields.get(inputName)
                if field:
                    field.error = "Daily rate cannot be less than $1"

                return False

        
        return True
    
    shouldRunInsert = True

    for fieldName, inputField in inputFields.items():
        if isValidInput(fieldName, inputField.value):
            inputField.error = None
        else:
            shouldRunInsert = False
            

    if not vehicleTypeDropdown.value:
        vehicleTypeDropdown.error_text = "Please select a vehicle type"
        shouldRunInsert = False
    else:
        vehicleTypeDropdown.error_text = None

    if shouldRunInsert:
        licensePlate = inputFields[VehicleInputField.LICENSE_PLATE].value
        make = inputFields[VehicleInputField.MAKE].value
        model = inputFields[VehicleInputField.MODEL].value
        color = inputFields[VehicleInputField.COLOR].value
        dailyRate = float(inputFields[VehicleInputField.DAILY_RATE].value)
        year = int(inputFields[VehicleInputField.YEAR].value)
        mileage = int(inputFields[VehicleInputField.MILEAGE].value)
        branchId = int(inputFields[VehicleInputField.BRANCH_ID].value)
        # python typechecker insists value is nullable when
        # its null-checked earlier on, so im casting this
        vehicleType = cast(str, vehicleTypeDropdown.value)

        vehicleTypeId = getVehicleTypeId(cursor, vehicleType)
        if vehicleTypeId < 0:
            print("VehicleType input was a value that does not exist in the database! Query failed.")
            return
        
        query = "SELECT 1 FROM Vehicle WHERE LicensePlate = %s"
        params = (licensePlate,)
        error = performSafeQuery(cursor, query, params)
        if error is not None:
            resultText.color = ft.Colors.RED
            resultText.value = str(error)
            return
        elif cursor.fetchone() is not None:
            resultText.color = ft.Colors.RED
            resultText.value = "Car with license plate already exists."
            return

        # the super query
        query = """
            INSERT INTO Vehicle (LicensePlate, Make, Model, Color, DailyRate, Year, CurrentMileage, BranchID, VehicleTypeID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (licensePlate, make, model, color, dailyRate, year, mileage, branchId, vehicleTypeId,)
        error = performSafeQuery(cursor, query, params)
            
        if error:
            resultText.color = ft.Colors.RED
            resultText.value = str(error)
            return

        resultText.color = ft.Colors.GREEN
        resultText.value = "Successfully inserted vehicle"
        database.commit()


# helper function to build all of the UI for the vehicle input section
def prepareVehicleInputFields(screenWidth):
    FIFTH_SCREEN_WIDTH = screenWidth / 5

    # only allows digits 0-9, 0-4 characters in length
    # by the time years surpass 9999, this software will definitely
    # be deprecated
    YearInputFilter = ft.InputFilter(regex_string=r"^[0-9]{0,4}$")
    # accepts digits of any length
    NumbersInputFilter = ft.NumbersOnlyInputFilter()
    # accepts any characters, up to 20 characters
    LicensePlateInputFilter = ft.InputFilter(regex_string=r"^.{0,20}$")
    # accepts any characters, up to 50 characters
    FiftyCharLimitInputFilter = ft.InputFilter(regex_string=r"^.{0,50}$")
    # accepts any characters, up to 30 characters
    ThirtyCharLimitInputFilter = ft.InputFilter(regex_string=r"^.{0,30}$")
    # accepts up to 6 preceding numbers, an optional decimal point, and two optional numbers after the decimal
    DailyRateInputFilter = ft.InputFilter(regex_string=r"^\d{0,6}(\.\d{0,2})?$")

    vehicleInputHeader = ft.Text(
        "Fill in all of the fields and hit the submit button below to add a new vehicle to the database.", 
        width=FIFTH_SCREEN_WIDTH, 
        color="#000000", 
        text_align=ft.TextAlign.CENTER,
    )
    plateInput = ft.TextField(
        label="License Plate",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
        input_filter=LicensePlateInputFilter,
    )
    carMakeInput = ft.TextField(
        label="Car Make",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
        input_filter=FiftyCharLimitInputFilter,
    )
    carModelInput = ft.TextField(
        label="Car Model",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
        input_filter=FiftyCharLimitInputFilter,
    )
    carYearInput = ft.TextField(
        label="Car Year",
        color="#000000",
        input_filter=YearInputFilter,
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )
    carColorInput = ft.TextField(
        label="Car Color",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
        input_filter=ThirtyCharLimitInputFilter,
    )
    dailyRateInput = ft.TextField(
        label="Daily Rate",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
        input_filter=DailyRateInputFilter,
    )
    currentMileageInput = ft.TextField(
        label="Mileage",
        color="#000000",
        input_filter=NumbersInputFilter,
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )
    branchIdInput = ft.TextField(
        label="Branch ID",
        color="#000000",
        input_filter=NumbersInputFilter,
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )

    # car type is a dropdown since it pulls from a determined VehicleType table
    carTypeInput = ft.Dropdown(
        options=[
            ft.DropdownOption(VehicleType.SEDAN.value),
            ft.DropdownOption(VehicleType.SUV.value),
            ft.DropdownOption(VehicleType.VAN.value),
            ft.DropdownOption(VehicleType.TRUCK.value),
        ],
        color="#000000",
        hint_text="Vehicle Type",
        width=FIFTH_SCREEN_WIDTH,
        helper_text=" "
    )

    inputFields = {
        VehicleInputField.LICENSE_PLATE: plateInput,  
        VehicleInputField.MAKE: carMakeInput, 
        VehicleInputField.MODEL: carModelInput, 
        VehicleInputField.YEAR: carYearInput, 
        VehicleInputField.COLOR: carColorInput, 
        VehicleInputField.DAILY_RATE: dailyRateInput, 
        VehicleInputField.MILEAGE: currentMileageInput, 
        VehicleInputField.BRANCH_ID: branchIdInput,
    }

    resultText = ft.Text(
        "", 
        width=FIFTH_SCREEN_WIDTH, 
        color="#000000", 
        text_align=ft.TextAlign.CENTER,
    )

    submitCarButton = ft.Button(
        content="Submit", 
        on_click=lambda e: onVehicleInputSubmit(inputFields, carTypeInput, resultText), 
        width=FIFTH_SCREEN_WIDTH
    )

    # formatting is a pain
    vehicleInputFieldGrid = ft.Column(
        controls=[
            ft.Row([branchIdInput, plateInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([carMakeInput, carModelInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([carYearInput, carColorInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([dailyRateInput, currentMileageInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([carTypeInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    vehicleInputColumn = ft.Column(
        controls=[
            ft.Column(
                controls=[
                    vehicleInputHeader,
                    vehicleInputFieldGrid,
                    submitCarButton,
                    resultText,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],

        alignment=ft.MainAxisAlignment.CENTER,
    )

    return vehicleInputColumn

# called when the user presses the button to query the database and return
# agreements that are all connected to the customer's ID
def onCustomerAgreementSearch(customerInput: ft.TextField, output: ft.ListView):
    output.controls.clear()

    if customerInput.value.strip() == "":
        customerInput.error = "Please enter a customer ID"
        return
    else:
        customerInput.error = None

    # i know the customer ID input only accepts numbers, so this should never throw,
    # but im gonna play it safe
    customerId = None
    try:
        customerId = int(customerInput.value)
    except ValueError:
        return
    
    agreementElements = []

    
    columnsToGet = """
        AgreementID, RentalAgreement.VehicleID, PickupBranchID, ReturnBranchID, 
        ScheduledPickup, ScheduledReturn, ActualPickup, ActualReturn, EstimatedCost, 
        ActualCost, Status, Vehicle.LicensePlate, Vehicle.Make, Vehicle.Model, Vehicle.Color, Vehicle.Year
    """
    query = f"SELECT {columnsToGet} FROM RentalAgreement JOIN Vehicle ON RentalAgreement.VehicleID = Vehicle.VehicleID WHERE CustomerID = %s"
    params = (customerId,)
    error = performSafeQuery(cursor, query, params)

    if error is not None:
        print(error)
        return
    
    results = cursor.fetchall()

    #error message for invalid CustomerID
    if len(results) == 0:
        output.controls = [
            ft.Text(
                "Invalid customer ID or no agreements found.",
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.RED,
                height=150,
            )
        ]
        output.update()
        return
    
    for result in results:
        agreementId = result[0]
        vehicleId = result[1]
        pickupBranchId = result[2]
        returnBranchId = result[3]
        scheduledPickup = result[4]
        scheduledReturn = result[5]
        actualPickup = result[6]
        actualReturn = result[7]
        estimatedCost = result[8]
        actualCost = result[9]
        status = result[10]
        licensePlate = result[11]
        make = result[12]
        model = result[13]
        color = result[14]
        year = result[15]

        if estimatedCost is None:
            query = """
                SELECT Vehicle.DailyRate
                FROM RentalAgreement
                JOIN Vehicle ON RentalAgreement.VehicleID = Vehicle.VehicleID
                WHERE RentalAgreement.AgreementID = %s
            """
            params = (result[0],)
            error = performSafeQuery(cursor, query, params)

            if error is None:
                result = cursor.fetchone()
                dailyRate = None
                if result is not None:
                    dailyRate = cast(float, result[0])
                
                estimatedCost = None
                actualCost = None
                if dailyRate is not None:
                    dailyRate = float(dailyRate)
                    estimatedCost = getEstimatedCost(cast(datetime, scheduledPickup), cast(datetime, scheduledReturn), dailyRate)
                    if actualPickup and actualReturn:
                        actualCost = getEstimatedCost(cast(datetime, actualPickup), cast(datetime, actualReturn), dailyRate)
            else:
                print(error)

        if actualCost:
            actualCost = f"${actualCost:.2f}"
        else:
            actualCost = "Not calculated"

        textContent = (
            f"Agreement ID: {agreementId} | "
            f"Vehicle ID: {vehicleId}\n"
            f"Pickup Branch ID: {pickupBranchId} | "
            f"Return Branch ID: {returnBranchId}\n"
            f"Scheduled Pickup: {scheduledPickup}\n"
            f"Scheduled Return: {scheduledReturn}\n"
            f"Actual Pickup: {actualPickup or 'Not picked up'}\n"
            f"Actual Return: {actualReturn or 'Not returned'}\n"
            f"Estimated Cost: ${estimatedCost:.2f}\n"
            f"Actual Cost: {actualCost}\n"
            f"Status: {status}\n"
            f"Vehicle: {year} {make} {model} ({color}) | Plate: {licensePlate}\n"
        )
        resultText = ft.Text(
            value=textContent, 
            text_align=ft.TextAlign.CENTER,
            align=ft.Alignment.CENTER,
            color=ft.Colors.BLACK,
            height=150,
            size=10,
            expand=True,
        )

        agreementElements.append(resultText)


    output.controls = agreementElements
    output.update()

# helper function to build all of the UI for the customer agreement viewer section
def prepareCustomerAgreementViewer(screenWidth):
    THIRD_SCREEN_WIDTH = screenWidth / 3
    FIFTH_SCREEN_WIDTH = screenWidth / 5

    CustomerIdInputFilter = ft.NumbersOnlyInputFilter()

    customerAgreementHeader = ft.Text(
        "Fill in the field below with a valid customer ID and press the button to list all of their active rental agreements", 
        width=FIFTH_SCREEN_WIDTH, 
        color="#000000", 
        text_align=ft.TextAlign.CENTER,
    )

    customerIdInput = ft.TextField(
        label="Customer ID",
        color="#000000",
        input_filter=CustomerIdInputFilter,
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )

    agreementsListView = ft.ListView(
        controls = [
            ft.Text(
                "Enter an ID to load agreements.", 
                text_align=ft.TextAlign.CENTER,
                align=ft.Alignment.CENTER,
                color=ft.Colors.BLACK,
                height=150,
            ),
        ],
        height = 2 * 150,
        spacing=0,
        width=THIRD_SCREEN_WIDTH,
        scroll=ft.ScrollMode.ALWAYS,
    )

    agreementsBorderContainer = ft.Container(
        content=agreementsListView,
        border=ft.Border(ft.BorderSide(), ft.BorderSide(), ft.BorderSide(), ft.BorderSide()),
    )

    getAgreementsButton = ft.Button(
        content="Search", 
        on_click=lambda e: onCustomerAgreementSearch(customerIdInput, agreementsListView), 
        width=FIFTH_SCREEN_WIDTH
    )

    customerAgreementColumn = ft.Column(
        controls=[
            ft.Column(
                controls=[
                    customerAgreementHeader,
                    customerIdInput,
                    getAgreementsButton,
                    agreementsBorderContainer,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],

        alignment=ft.MainAxisAlignment.CENTER,
    )

    return customerAgreementColumn


ft.run(main)
