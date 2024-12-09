import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import csv
import tkinter as tk
from tkcalendar import Calendar

# Function to select a date using a calendar
def pick_date(prompt):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    date_window = tk.Toplevel(root)
    date_window.title(prompt)
    cal = Calendar(date_window, date_pattern="dd-mm-yy")
    cal.pack(pady=20)

    def select_date():
        selected_date = cal.get_date()
        date_window.destroy()
        root.quit()
        root.destroy()
        return selected_date

    tk.Button(date_window, text="Select", command=select_date).pack(pady=20)
    root.mainloop()
    return cal.get_date()

# Step 1: Gather inputs from the user
def get_inputs():
    print("Please select the start date.")
    start_date = pick_date("Select Start Date")

    print("Please select the end date.")
    end_date = pick_date("Select End Date")

    stores_csv = "Data/stores.csv"
    items_csv = "Data/items.csv"
    return start_date, end_date, stores_csv, items_csv

# Step 2: Load data from CSVs
def load_csv_data(stores_csv, items_csv):
    stores = []
    items = []

    with open(stores_csv, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            shop_name = row[0]
            shop_address = row[1]
            stores.append({
                "shop_name": shop_name.strip(),
                "shop_address": shop_address.strip()
            })

    with open(items_csv, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            item_name = row[0]
            unit_price = row[1]
            items.append({
                "item_name": item_name.strip(),
                "unit_price": float(unit_price.strip())
            })

    return stores, items

# Step 3: Randomly generate receipts
def generate_random_receipt_data(start_date, end_date, stores, items):
    date_format = "%d-%m-%y"
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    
    receipts = []
    num_receipts = int(input("How many receipts would you like to generate? "))
    for _ in range(num_receipts):
        store = random.choice(stores)
        date = start + timedelta(days=random.randint(0, (end - start).days))
        receipt_number = random.randint(10000, 99999999)  # Generate 5 to 8 digit receipt number
        selected_items = random.sample(items, k=random.randint(3, 12))
        receipt_items = []
        total = 0

        for item_data in selected_items:
            units = random.randint(1, 2)
            cost = item_data['unit_price'] * units
            receipt_items.append({
                "item_name": item_data['item_name'],
                "units": units,
                "cost": cost
            })
            total += round(cost, 2)

        total = round(total, 2)
        vat = round(total - (total / 1.2), 2)

        receipts.append({
            "shop_name": store['shop_name'],
            "shop_address": store['shop_address'],
            "date": random.choice([
                date.strftime('%d-%m-%Y'),
                date.strftime('%d %b %y'),
                date.strftime('%d/%m/%y')
            ]) + (f" {random.randint(9, 22):02d}:{random.randint(0, 59):02d}" if random.choice([True, False]) else ""),
            "receipt_number": receipt_number,
            "items": receipt_items,
            "total": total,
            "vat": vat,
            "thank_you_message": random.choice([
                "Thank you!",
                "See you soon",
                "Thanks for your custom",
                ""
            ]),
            "show_receipt_number": random.choice([True, False]),
            "show_receipt_label": random.choice([True, False])
        })
    
    return receipts

# Step 4: Render receipts to JPG
def render_receipts(receipts):
    fonts = ["receipt1.ttf", "receipt2.ttf", "receipt3.ttf", "receipt4.ttf", "receipt5.ttf", "receipt6.ttf", "receipt7.otf", "receipt8.otf", "receipt9.otf", "receipt10.otf"]

    for i, receipt in enumerate(receipts):
        font_path = "Fonts/" + random.choice(fonts)
        font_size_shop = random.randint(10, 14)
        font_size_items = 12
        line_spacing = random.randint(18, 25)
        text_alignment_shop = random.choice(["left", "center"])
        address_multiline = random.choice([True, False])
        receipt_number_position = random.choice(["top", "bottom"])

        image = Image.new("RGB", (400, 600), "white")
        draw = ImageDraw.Draw(image)

        try:
            font_shop = ImageFont.truetype(font_path, font_size_shop)
            font_items = ImageFont.truetype(font_path, font_size_items)
        except Exception as e:
            print(f"Font error: {e}. Default font used.")
            font_shop = font_items = ImageFont.load_default()

        y = 20
        x_left = 10
        x_center = 200

        def draw_text(text, y_pos, alignment="left", bold=False):
            font = font_shop if bold else font_items
            if alignment == "left":
                draw.text((x_left, y_pos), text, font=font, fill="black")
            elif alignment == "center":
                text_width = draw.textlength(text, font=font)
                draw.text((x_center - text_width // 2, y_pos), text, font=font, fill="black")

        # Receipt number at the top (if applicable)
        if receipt_number_position == "top" and receipt['show_receipt_number']:
            receipt_text = f"Receipt#: {receipt['receipt_number']}" if receipt['show_receipt_label'] else f"{receipt['receipt_number']}"
            draw_text(receipt_text, y, alignment="left")
            y += line_spacing * random.uniform(0.8, 1.2)

        # Shop name
        draw_text(f"{receipt['shop_name']}", y, alignment=text_alignment_shop, bold=True)
        y += line_spacing

        # Address with random multiline option
        if address_multiline:
            for line in receipt['shop_address'].split(', '):
                draw_text(line, y, alignment=text_alignment_shop)
                y += line_spacing
        else:
            draw_text(receipt['shop_address'], y, alignment=text_alignment_shop)
            y += line_spacing

        # Date
        draw_text(receipt['date'], y, alignment="left")
        y += line_spacing * random.uniform(1.2, 1.8)

        # Items
        draw_text("Items:", y)
        y += line_spacing
        for item in receipt['items']:
            draw_text(f"{item['item_name']:20} x{item['units']} \u00A3{item['cost']:.2f}", y, alignment="left")
            y += line_spacing

        # Total and VAT
        y += line_spacing * 1.5
        draw_text(f"Total: \u00A3{receipt['total']:.2f}", y, alignment="left", bold=True)
        y += line_spacing
        draw_text(f"VAT (20%): \u00A3{receipt['vat']:.2f}", y, alignment="left")

        # Thank-you message
        if receipt['thank_you_message']:
            y += line_spacing * 1.5
            draw_text(receipt['thank_you_message'], y, alignment="left")

        # Receipt number at the bottom (if applicable)
        if receipt_number_position == "bottom" and receipt['show_receipt_number']:
            y += line_spacing * 1.5
            receipt_text = f"Receipt#: {receipt['receipt_number']}" if receipt['show_receipt_label'] else f"{receipt['receipt_number']}"
            draw_text(receipt_text, y, alignment="left")

        # Save image
        image.save(f"Generated/{receipt['receipt_number']}.jpg")
        print(f"Receipt {i+1} saved as {receipt['receipt_number']}.jpg")

# Main execution
if __name__ == "__main__":
    start_date, end_date, stores_csv, items_csv = get_inputs()
    stores, items = load_csv_data(stores_csv, items_csv)
    receipts = generate_random_receipt_data(start_date, end_date, stores, items)
    render_receipts(receipts)
