def fix_str(text, length):
    """ตัด/เติม string ให้พอดีความยาว"""
    return text.encode("utf-8")[:length].ljust(length, b'\x00')


def add_book(filename="books.dat"):
    """เพิ่มข้อมูลหนังสือใหม่ (binary record)"""
    book_id = int(input("Enter Book ID: "))
    title = input("Enter Title: ")
    author = input("Enter Author: ")
    publisher = input("Enter Publisher: ")
    year = int(input("Enter Year Published: "))
    total = int(input("Enter Total Copies: "))
    avail = int(input("Enter Available Copies: "))
    price = float(input("Enter Price (THB): "))

    record = (
        book_id.to_bytes(4, "little") +
        fix_str(title, 20) +
        fix_str(author, 20) +
        fix_str(publisher, 20) +
        year.to_bytes(4, "little") +
        total.to_bytes(4, "little") +
        avail.to_bytes(4, "little") +
        fix_str(f"{price:.2f}", 8)  
    )

    with open(filename, "ab") as f:
        f.write(record)
    print("Book added successfully!")


def add_member(filename="members.dat"):
    # เพิ่มข้อมูลสมาชิก
    member_id = int(input("Enter Member ID: "))
    full_name = input("Enter Full Name: ")
    address = input("Enter Address: ")
    phone = input("Enter Phone: ")
    email = input("Enter Email: ")
    join_year = int(input("Enter Join Year: "))

    record = (
        member_id.to_bytes(4, "little") +
        fix_str(full_name, 20) +
        fix_str(address, 20) +
        fix_str(phone, 10) +
        fix_str(email, 30) +
        join_year.to_bytes(4, "little")
    )

    with open(filename, "ab") as f:
        f.write(record)
    print("Member added successfully!")



def view_books(filename="books.dat"):
    # แสดงข้อมูลหนังสือ
    record_size = 4 + 20 + 20 + 20 + 4 + 4 + 4 + 8
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(record_size):
                book_id   = int.from_bytes(chunk[0:4], "little")
                title     = chunk[4:24].decode("utf-8").strip("\x00 ")
                author    = chunk[24:44].decode("utf-8").strip("\x00 ")
                publisher = chunk[44:64].decode("utf-8").strip("\x00 ")
                year      = int.from_bytes(chunk[64:68], "little")
                total     = int.from_bytes(chunk[68:72], "little")
                avail     = int.from_bytes(chunk[72:76], "little")
                price     = chunk[76:84].decode("utf-8").strip("\x00 ")

                print(f"{book_id} | {title} | {author} | {publisher} | {year} | {total}/{avail} | {price} THB")
    except FileNotFoundError:
        print("No books.dat file found.")


def view_members(filename="members.dat"):
    # แสดงข้อมูลสมาชิก
    record_size = 4 + 20 + 20 + 10 + 30 + 4
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(record_size):
                member_id = int.from_bytes(chunk[0:4], "little")
                full_name = chunk[4:24].decode("utf-8").strip("\x00 ")
                address   = chunk[24:44].decode("utf-8").strip("\x00 ")
                phone     = chunk[44:54].decode("utf-8").strip("\x00 ")
                email     = chunk[54:84].decode("utf-8").strip("\x00 ")
                join_year = int.from_bytes(chunk[84:88], "little")

                print(f"{member_id} | {full_name} | {address} | {phone} | {email} | {join_year}")
    except FileNotFoundError:
        print("No members.dat file found.")
