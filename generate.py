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
    item_lists = {
        "christmas.csv": "Christmas",
        "easter.csv": "Easter",
        "cleaning.csv": "Cleaning",
        "grocery.csv": "Grocery"
    }

    include_item_lists = {}
    for item_list, name in item_lists.items():
        include = input(f"Include {name} items (y/n)? ")
        include_item_lists[item_list] = include.lower() == "y"

    return start_date, end_date, stores_csv, include_item_lists

# Step 2: Load data from CSVs
def load_csv_data(stores_csv, include_item_lists):
    stores = []
    items = []
    all_items = []

    with open(stores_csv, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            shop_name = row[0]
            shop_address = row[1]
            stores.append({
                "shop_name": shop_name.strip(),
                "shop_address": shop_address.strip()
            })

    for item_list, include in include_item_lists.items():
        if include:
            temp_items = []
            try:
                with open(f"Data/{item_list}", mode='r', encoding='utf-8-sig') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    for row in reader:
                        item_name = row[0]
                        unit_price = row[1]
                        temp_items.append({
                            "item_name": item_name.strip(),
                            "unit_price": float(unit_price.strip())
                        })
                all_items.append(temp_items)
            except FileNotFoundError:
                print(f"Warning: File Data/{item_list} not found. Skipping.")

    if not all_items:
        print("No item lists selected. Exiting.")
        exit()
    
    for item_list in all_items:
        items.extend(item_list)

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
        receipt_number = random.randint(10000, 99999999)
        selected_items = random.sample(items, k=random.randint(1, min(len(items), 12)))

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
    fonts = [
        "receipt1.ttf", "receipt2.ttf", "receipt3.ttf", "receipt4.ttf",
        "receipt5.ttf", "receipt6.ttf", "receipt7.ttf", "receipt8.ttf",
        "receipt9.ttf", "receipt10.ttf", "receipt11.ttf", "receipt12.ttf",
        "receipt13.ttf", "receipt14.ttf", "receipt15.ttf", "receipt16.ttf",
        "receipt17.otf", "receipt18.otf", "receipt19.otf", "receipt20.otf", "receipt21.otf"
    ]

    for i, receipt in enumerate(receipts):
        font_path = "Fonts/" + random.choice(fonts)
        font_size_shop = random.randint(16, 20)
        font_size_items = 12
        line_spacing = random.randint(18, 25)
        text_alignment_shop = random.choice(["left", "center"])
        address_multiline = random.choice([True, False])
        receipt_number_position = random.choice(["top", "bottom"])

        # Randomly decide whether to show a border
        show_border = random.choice([True, False])
        border_char = random.choice(["*", "#", "-", ".", "="]) if show_border else None

        # Generate a random background color in the range #ffffff to #f5f5f5
        bg_shade = random.randint(245, 255)
        bg_color = (bg_shade, bg_shade, bg_shade)

        # Fixed image size
        image_width = 400
        image_height = 600
        image = Image.new("RGB", (image_width, image_height), bg_color)
        draw = ImageDraw.Draw(image)

        try:
            font_shop = ImageFont.truetype(font_path, font_size_shop)
            font_items = ImageFont.truetype(font_path, font_size_items)

            # Test if the '£' symbol can be rendered by measuring its size
            supports_pound = draw.textlength("£", font=font_items) > 0
        except Exception as e:
            print(f"Font error: {e}. Default font used.")
            font_shop = font_items = ImageFont.load_default()
            supports_pound = False

        y = 10
        x_left = 10
        x_center = image_width // 2

        def draw_text(text, y_pos, alignment="left", bold=False):
            """Render text to the final image."""
            font = font_shop if bold else font_items
            if alignment == "left":
                draw.text((x_left, y_pos), text, font=font, fill="black")
            elif alignment == "center":
                text_width = draw.textlength(text, font=font)
                draw.text((x_center - text_width // 2, y_pos), text, font=font, fill="black")

        # Select a consistent quantity format for this receipt
        quantity_format = random.choice([
            "x{units}",  # x2
            "{units}x",  # 2x
            "{units} -",  # 2 -
            "{units} @"  # 2 @
        ])

        # Add border at the top
        if border_char:
            draw_text(border_char * (image_width // 10), y, alignment="center", bold=True)
            y += line_spacing

        # Receipt number at the top (if applicable)
        if receipt_number_position == "top" and receipt['show_receipt_number']:
            receipt_text = f"Receipt#: {receipt['receipt_number']}" if receipt['show_receipt_label'] else f"{receipt['receipt_number']}"
            draw_text(receipt_text, y)
            y += line_spacing * random.uniform(0.8, 1.2)

        # Shop name
        draw_text(receipt['shop_name'], y, alignment=text_alignment_shop, bold=True)
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
        draw_text(receipt['date'], y)
        y += line_spacing

        # Items
        draw_text("Items:", y)
        y += line_spacing
        for item in receipt['items']:
            cost_display = f"£{item['cost']:.2f}" if supports_pound else f"{item['cost']:.2f}"
            draw_text(
                f"{item['item_name']:20} {quantity_format.format(units=item['units'])} {cost_display}", y
            )
            y += line_spacing

        # Total and VAT
        y += line_spacing * 1.5
        total_display = f"£{receipt['total']:.2f}" if supports_pound else f"{receipt['total']:.2f}"
        draw_text(f"Total: {total_display}", y, bold=True)
        y += line_spacing
        vat_display = f"£{receipt['vat']:.2f}" if supports_pound else f"{receipt['vat']:.2f}"
        draw_text(f"VAT (20%): {vat_display}", y)
        y += line_spacing

        # Thank-you message
        if receipt['thank_you_message']:
            draw_text(receipt['thank_you_message'], y)
            y += line_spacing

        # Receipt number at the bottom (if applicable)
        if receipt_number_position == "bottom" and receipt['show_receipt_number']:
            receipt_text = f"Receipt#: {receipt['receipt_number']}" if receipt['show_receipt_label'] else f"{receipt['receipt_number']}"
            draw_text(receipt_text, y)
            y += line_spacing

        # Add border at the bottom
        if border_char:
            draw_text(border_char * (image_width // 10), y, alignment="center", bold=True)

        # Save image
        image.save(f"Generated/{receipt['receipt_number']}.jpg")
        print(f"Receipt {i + 1} saved as {receipt['receipt_number']}.jpg")



# Main execution
if __name__ == "__main__":
    start_date, end_date, stores_csv, include_item_lists = get_inputs()
    stores, items = load_csv_data(stores_csv, include_item_lists)
    receipts = generate_random_receipt_data(start_date, end_date, stores, items)
    render_receipts(receipts)