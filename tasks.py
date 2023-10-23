import os
from robocorp.tasks import task
from robocorp import browser
from RPA.PDF import PDF
import shutil
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from robot.libraries.BuiltIn import BuiltIn


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=2000)
    page = browser.page()
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        print(row)
        order_number = str(row["Order number"])
        preview_path = fill_form(row, order_number)
        while page.locator("#order").is_visible():
            page.click("#order")
        receipt_path = screenshot_receipt(order_number)
        list_of_files = [receipt_path, preview_path]
        create_pdf(list_of_files, order_number)
        page.click("#order-another")
        archive_receipts()


def open_robot_order_website():
    # TODO: Implement your function here
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)
    return orders


def close_annoying_modal():
    page = browser.page()
    page.click("text=Yep")


def fill_form(row, order_number):
    page = browser.page()
    page.select_option("#head", row["Head"])
    page.click(f"#id-body-{row['Body']}")
    page.get_by_placeholder("Enter the part number for the legs").fill(str(row["Legs"]))
    page.fill("#address", row["Address"])
    page.click("#preview")
    page.wait_for_selector("#robot-preview-image")

    page.locator("#robot-preview-image").screenshot(
        path=f"output/robot-preview-{order_number}.png"
    )
    return f"output/robot-preview-{order_number}.png"


def screenshot_receipt(order_number):
    page = browser.page()
    page.wait_for_selector("#receipt")
    page.locator("#receipt").screenshot(path=f"output/receipt-{order_number}.png")
    return f"output/receipt-{order_number}.png"


def create_pdf(filelist, order_number):
    path = "./output/PDF"
    pdf = PDF()

    if os.path.isdir("output/PDF/"):
        pdf.add_files_to_pdf(filelist, f"output/PDF/output_{order_number}.pdf")
    else:
        os.makedirs(path)
        pdf.add_files_to_pdf(filelist, f"output/PDF/output_{order_number}.pdf")


def archive_receipts():
    shutil.make_archive("receipts", "zip", "./output/PDF")
