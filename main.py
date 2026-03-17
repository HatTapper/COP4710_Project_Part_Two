import flet as ft
import mysql.connector
from definitions import VehicleInputField, VehicleType

# note, this assumes the database is already constructed
# at some point, we could write init code to prepare the tables
# if they don't exist in the database

# replace parameters with your data
DB_HOST_NAME = "localhost"
DB_USER_NAME = "root"
DB_USER_PASS = "6432"
DB_DATABASE_NAME = "vrms"

mydb = mysql.connector.connect(
    host=DB_HOST_NAME,
    user=DB_USER_NAME,
    password=DB_USER_PASS,
    database=DB_DATABASE_NAME,
)

# cursor handles all queries and received data from the database
mycursor = mydb.cursor()

# this is run by flet at startup, treat as a standard main function
def main(page: ft.Page):
    SCREEN_WIDTH = page.window.width
    SCREEN_HEIGHT = page.window.height

    if SCREEN_WIDTH == None or SCREEN_HEIGHT == None:
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

# called when the button to submit Vehicle table data is pressed, requires the dict of input fields that
# fulfill the table data and the dropdown
def onVehicleInputSubmit(inputFields: dict[VehicleInputField, ft.TextField], vehicleTypeDropdown: ft.Dropdown):
    # TODO: needs to check each field for if the data is valid before running the SQL query
    for fieldName, inputField in inputFields.items():
        if inputField.value.strip() == "":
            inputField.error = "This field is required"
        else:
            inputField.error = None

    if not vehicleTypeDropdown.value:
        vehicleTypeDropdown.error_text = "Please select a vehicle type"
    else:
        vehicleTypeDropdown.error_text = None

    # TODO: update query so it inserts into Vehicle table once data has been verified
    mycursor.execute("SELECT * FROM customer")
    print(mycursor.fetchall())

# helper function to build all of the UI for the vehicle input section
def prepareVehicleInputFields(screenWidth):
    FIFTH_SCREEN_WIDTH = screenWidth / 5

    # only allows digits 0-9, 0-4 characters in length
    # by the time years surpass 9999, this software will definitely
    # be deprecated
    YearInputFilter = ft.InputFilter(regex_string=r"^[0-9]{0,4}$")
    # accepts digits of any length
    MileageInputFilter = ft.NumbersOnlyInputFilter()

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
    )
    carNameInput = ft.TextField(
        label="Car Name",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )
    carMakeInput = ft.TextField(
        label="Car Make",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )
    carModelInput = ft.TextField(
        label="Car Model",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
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
    )
    dailyRateInput = ft.TextField(
        label="Daily Rate",
        color="#000000",
        width=FIFTH_SCREEN_WIDTH,
        helper=" ",
    )
    currentMileageInput = ft.TextField(
        label="Mileage",
        color="#000000",
        input_filter=MileageInputFilter,
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
        VehicleInputField.NAME: carNameInput, 
        VehicleInputField.MAKE: carMakeInput, 
        VehicleInputField.MODEL: carModelInput, 
        VehicleInputField.YEAR: carYearInput, 
        VehicleInputField.COLOR: carColorInput, 
        VehicleInputField.DAILY_RATE: dailyRateInput, 
        VehicleInputField.MILEAGE: currentMileageInput, 
    }

    submitCarButton = ft.Button(
        content="Submit", 
        on_click=lambda e: onVehicleInputSubmit(inputFields, carTypeInput), 
        width=FIFTH_SCREEN_WIDTH
    )

    # formatting is a pain
    vehicleInputFieldGrid = ft.Column(
        controls=[
            ft.Row([carNameInput, plateInput], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
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
                    submitCarButton
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],

        alignment=ft.MainAxisAlignment.CENTER,
    )

    return vehicleInputColumn

# called when the user presses the button to query the database and return
# agreements that are all connected to the customer's ID
def onCustomerAgreementSearch(e: ft.Event, customerInput: ft.TextField, output: ft.ListView):
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
    
    # TODO: update query so it pulls from RentalAgreements table
    mycursor.execute("SELECT * FROM customer")
    print(mycursor.fetchall())

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
                height=50,
            ),
        ],
        height = 6 * 50,
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
        on_click=lambda e: onCustomerAgreementSearch(e, customerIdInput, agreementsListView), 
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
