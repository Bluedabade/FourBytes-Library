from module.utils import fix_str, from_str, to_i32, from_i32

BOOK_REC_SIZE = 88  

def _scan_max_id(filename):
    max_id = 0
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(BOOK_REC_SIZE):
                bid = from_i32(chunk[0:4])
                if bid > max_id:
                    max_id = bid
    except FileNotFoundError:
        pass
    return max_id

def get_next_book_id(filename="storage/books.dat"):
    return _scan_max_id(filename) + 1

def _find_record_pos_by_id(target_id, filename):
    try:
        with open(filename, "rb") as f:
            pos = 0
            while chunk := f.read(BOOK_REC_SIZE):
                bid = from_i32(chunk[0:4])
                if bid == target_id:
                    return pos, chunk
                pos += BOOK_REC_SIZE
    except FileNotFoundError:
        return -1, None
    return -1, None

def add_book(filename="storage/books.dat"):
    book_id = get_next_book_id(filename)
    print(f"Assigned Book ID: {book_id}")

    while True:
        year_str = input("Enter Year Published: ").strip()
        if year_str.isdigit() and int(year_str) > 0:
            year = int(year_str)
            break
        print("Invalid year. Please enter a positive number.")

    while True:
        total_str = input("Enter Total Copies: ").strip()
        if total_str.isdigit() and int(total_str) >= 0:
            total = int(total_str)
            break
        print("Invalid total copies. Must be a non-negative integer.")

    while True:
        avail_str = input("Enter Available Copies: ").strip()
        if avail_str.isdigit() and int(avail_str) >= 0:
            avail = int(avail_str)
            if avail <= total:
                break
            else:
                print("Available copies cannot exceed total copies.")
        else:
            print("Invalid available copies. Must be a non-negative integer.")

    while True:
        price_str = input("Enter Price (THB): ").strip()
        try:
            price = float(price_str)
            if price >= 0:
                break
            else:
                print("Price must be non-negative.")
        except ValueError:
            print("Invalid price. Please enter a number.")

    while True:
        title = input("Enter Title: ").strip()
        if title:
            break
        print("Title cannot be empty.")
    while True:
        author = input("Enter Author: ").strip()
        if author:
            break
        print("Author cannot be empty.")
    while True:
        publisher = input("Enter Publisher: ").strip()
        if publisher:
            break
        print("Publisher cannot be empty.")

    record = (
        to_i32(book_id) +
        fix_str(title, 20) +
        fix_str(author, 20) +
        fix_str(publisher, 20) +
        to_i32(year) +
        to_i32(total) +
        to_i32(avail) +
        fix_str(f"{price:.2f}", 8) +
        to_i32(0)   
    )
    with open(filename, "ab") as f:
        f.write(record)
    print("Book added successfully.")


def view_books(filename="storage/books.dat"):
    try:
        with open(filename, "rb") as f:
            print(f"{'ID':<5} {'Title':<20} {'Author':<20} {'Publisher':<20} {'Year':<6} {'Total':<6} {'Avail':<6} {'Price':<8}")
            print("-"*90)
            found = False
            while chunk := f.read(BOOK_REC_SIZE):
                deleted = from_i32(chunk[84:88])
                if deleted != 0:
                    continue
                book_id   = from_i32(chunk[0:4])
                title     = from_str(chunk[4:24])
                author    = from_str(chunk[24:44])
                publisher = from_str(chunk[44:64])
                year      = from_i32(chunk[64:68])
                total     = from_i32(chunk[68:72])
                avail     = from_i32(chunk[72:76])
                price     = from_str(chunk[76:84])
                print(f"{book_id:<5} {title:<20} {author:<20} {publisher:<20} {year:<6} {total:<6} {avail:<6} {price:<8}")
                found = True
            if not found:
                print("No active book records found.")
    except FileNotFoundError:
        print("No book records found.")


def update_book(filename="storage/books.dat"):
    try:
        target_id = int(input("Enter Book ID to update: ").strip())
    except ValueError:
        print("Invalid Book ID.")
        return

    pos, chunk = _find_record_pos_by_id(target_id, filename)
    if pos < 0 or chunk is None or from_i32(chunk[84:88]) != 0:
        print("Book not found.")
        return

    print("Leave blank to keep old value.")
    with open(filename, "r+b") as f:
        new_title = input("New Title: ").strip()
        if new_title:
            f.seek(pos + 4); f.write(fix_str(new_title, 20))
        new_author = input("New Author: ").strip()
        if new_author:
            f.seek(pos + 24); f.write(fix_str(new_author, 20))
        new_pub = input("New Publisher: ").strip()
        if new_pub:
            f.seek(pos + 44); f.write(fix_str(new_pub, 20))

        while True:
            new_year = input("New Year Published: ").strip()
            if not new_year:
                break
            if new_year.isdigit() and int(new_year) > 0:
                f.seek(pos + 64); f.write(to_i32(int(new_year)))
                break
            print("Invalid year. Please enter a positive number or leave blank.")

        cur_total = from_i32(chunk[68:72])
        cur_avail = from_i32(chunk[72:76])

        while True:
            new_total = input("New Total Copies: ").strip()
            if not new_total:
                break
            if new_total.isdigit() and int(new_total) >= 0:
                t = int(new_total)
                a = cur_avail
                if a > t:
                    print("Invalid: available copies > total copies.")
                else:
                    f.seek(pos + 68); f.write(to_i32(t))
                break
            print("Invalid total copies. Please enter non-negative integer or leave blank.")

        while True:
            new_avail = input("New Available Copies: ").strip()
            if not new_avail:
                break
            if new_avail.isdigit() and int(new_avail) >= 0:
                a = int(new_avail)
                t = int(new_total) if new_total else cur_total
                if a > t:
                    print("Invalid: available copies > total copies.")
                else:
                    f.seek(pos + 72); f.write(to_i32(a))
                break
            print("Invalid available copies. Please enter non-negative integer or leave blank.")

        while True:
            new_price = input("New Price (THB): ").strip()
            if not new_price:
                break
            try:
                p = float(new_price)
                if p >= 0:
                    f.seek(pos + 76); f.write(fix_str(f"{p:.2f}", 8))
                    break
                else:
                    print("Price must be non-negative.")
            except ValueError:
                print("Invalid price. Please enter a number or leave blank.")

    print("Book updated successfully.")


def delete_book(filename="storage/books.dat"):
    try:
        target_id = int(input("Enter Book ID to delete: ").strip())
    except ValueError:
        print("Invalid Book ID.")
        return

    pos, chunk = _find_record_pos_by_id(target_id, filename)
    if pos < 0 or chunk is None:
        print("Book not found.")
        return

    confirm = input(f"Are you sure you want to delete Book ID {target_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        with open(filename, "r+b") as f:
            f.seek(pos + 84)
            f.write(to_i32(1))
        print("Book deleted successfully.")
    except FileNotFoundError:
        print("No book records found.")

def book_exists_and_active(book_id, filename="storage/books.dat"):
    pos, chunk = _find_record_pos_by_id(book_id, filename)
    if pos < 0 or chunk is None: 
        return False
    return from_i32(chunk[84:88]) == 0

def get_book_avail(book_id, filename="storage/books.dat"):
    pos, chunk = _find_record_pos_by_id(book_id, filename)
    if pos < 0 or chunk is None: 
        return -1, -1, -1
    total = from_i32(chunk[68:72])
    avail = from_i32(chunk[72:76])
    return pos, total, avail

def set_book_avail_at_pos(pos, new_avail, filename="storage/books.dat"):
    with open(filename, "r+b") as f:
        f.seek(pos + 72)
        f.write(to_i32(new_avail))