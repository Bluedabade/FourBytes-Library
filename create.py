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

# ====== Helpers (ขนาดเรคคอร์ด/ออฟเซ็ต) ======
BOOK_REC_SIZE = 4 + 20 + 20 + 20 + 4 + 4 + 4 + 8
MEMB_REC_SIZE = 4 + 20 + 20 + 10 + 30 + 4

def _parse_book(chunk: bytes):
    return {
        "book_id":   int.from_bytes(chunk[0:4], "little"),
        "title":     chunk[4:24].decode("utf-8").strip("\x00 "),
        "author":    chunk[24:44].decode("utf-8").strip("\x00 "),
        "publisher": chunk[44:64].decode("utf-8").strip("\x00 "),
        "year":      int.from_bytes(chunk[64:68], "little"),
        "total":     int.from_bytes(chunk[68:72], "little"),
        "avail":     int.from_bytes(chunk[72:76], "little"),
        "price":     chunk[76:84].decode("utf-8").strip("\x00 "),
    }

def _build_book(d):
    return (
        int(d["book_id"]).to_bytes(4, "little") +
        fix_str(d["title"], 20) +
        fix_str(d["author"], 20) +
        fix_str(d["publisher"], 20) +
        int(d["year"]).to_bytes(4, "little") +
        int(d["total"]).to_bytes(4, "little") +
        int(d["avail"]).to_bytes(4, "little") +
        fix_str(f'{float(d["price"]):.2f}', 8)
    )

def _parse_member(chunk: bytes):
    return {
        "member_id": int.from_bytes(chunk[0:4], "little"),
        "full_name": chunk[4:24].decode("utf-8").strip("\x00 "),
        "address":   chunk[24:44].decode("utf-8").strip("\x00 "),
        "phone":     chunk[44:54].decode("utf-8").strip("\x00 "),
        "email":     chunk[54:84].decode("utf-8").strip("\x00 "),
        "join_year": int.from_bytes(chunk[84:88], "little"),
    }

def _build_member(d):
    return (
        int(d["member_id"]).to_bytes(4, "little") +
        fix_str(d["full_name"], 20) +
        fix_str(d["address"], 20) +
        fix_str(d["phone"], 10) +
        fix_str(d["email"], 30) +
        int(d["join_year"]).to_bytes(4, "little")
    )

# ====== READ (ค้นหา 1 รายการด้วย ID) ======
def find_book_by_id(book_id: int, filename="books.dat"):
    try:
        with open(filename, "rb") as f:
            pos = 0
            while chunk := f.read(BOOK_REC_SIZE):
                rec = _parse_book(chunk)
                if rec["book_id"] == book_id:
                    return pos, rec
                pos += BOOK_REC_SIZE
    except FileNotFoundError:
        pass
    return None, None

def find_member_by_id(member_id: int, filename="members.dat"):
    try:
        with open(filename, "rb") as f:
            pos = 0
            while chunk := f.read(MEMB_REC_SIZE):
                rec = _parse_member(chunk)
                if rec["member_id"] == member_id:
                    return pos, rec
                pos += MEMB_REC_SIZE
    except FileNotFoundError:
        pass
    return None, None

def search_book():
    try:
        bid = int(input("Enter Book ID to search: "))
    except ValueError:
        print("Invalid ID.")
        return
    pos, rec = find_book_by_id(bid)
    if rec:
        print(f'FOUND -> {rec["book_id"]} | {rec["title"]} | {rec["author"]} | {rec["publisher"]} | '
              f'{rec["year"]} | {rec["total"]}/{rec["avail"]} | {rec["price"]} THB')
    else:
        print("Book not found.")

def search_member():
    try:
        mid = int(input("Enter Member ID to search: "))
    except ValueError:
        print("Invalid ID.")
        return
    pos, rec = find_member_by_id(mid)
    if rec:
        print(f'FOUND -> {rec["member_id"]} | {rec["full_name"]} | {rec["address"]} | '
              f'{rec["phone"]} | {rec["email"]} | {rec["join_year"]}')
    else:
        print("Member not found.")

# ====== UPDATE (แก้ไขข้อมูลเฉพาะเรคคอร์ด) ======
def _prompt_keep(cur, label, cast=str):
    s = input(f"{label} [{cur}] (Enter=keep): ").strip()
    if s == "":
        return cur
    try:
        return cast(s)
    except Exception:
        print("Invalid input, keeping old value.")
        return cur

def update_book(filename="books.dat"):
    try:
        target = int(input("Enter Book ID to update: "))
    except ValueError:
        print("Invalid ID.")
        return

    pos, rec = find_book_by_id(target, filename)
    if not rec:
        print("Book not found.")
        return

    print("Current:", rec)
    # รับค่าที่จะแก้ (Enter เพื่อคงค่าเดิม)
    rec["title"]     = _prompt_keep(rec["title"], "Title")
    rec["author"]    = _prompt_keep(rec["author"], "Author")
    rec["publisher"] = _prompt_keep(rec["publisher"], "Publisher")
    rec["year"]      = _prompt_keep(rec["year"], "Year", int)
    rec["total"]     = _prompt_keep(rec["total"], "Total Copies", int)
    rec["avail"]     = _prompt_keep(rec["avail"], "Available Copies", int)
    rec["price"]     = _prompt_keep(rec["price"], "Price (THB)")

    data = _build_book(rec)
    with open(filename, "r+b") as f:
        f.seek(pos)
        f.write(data)
    print("Book updated successfully.")

def update_member(filename="members.dat"):
    try:
        target = int(input("Enter Member ID to update: "))
    except ValueError:
        print("Invalid ID.")
        return

    pos, rec = find_member_by_id(target, filename)
    if not rec:
        print("Member not found.")
        return

    print("Current:", rec)
    rec["full_name"] = _prompt_keep(rec["full_name"], "Full Name")
    rec["address"]   = _prompt_keep(rec["address"], "Address")
    rec["phone"]     = _prompt_keep(rec["phone"], "Phone")
    rec["email"]     = _prompt_keep(rec["email"], "Email")
    rec["join_year"] = _prompt_keep(rec["join_year"], "Join Year", int)

    data = _build_member(rec)
    with open(filename, "r+b") as f:
        f.seek(pos)
        f.write(data)
    print("Member updated successfully.")

# ====== DELETE (ลบเรคคอร์ดด้วยการเขียนไฟล์ใหม่) ======
import os, tempfile

def _rewrite_without_id(filename, rec_size, get_id_fn, target_id):
    if not os.path.exists(filename):
        print("File not found.")
        return False

    fd, tmpname = tempfile.mkstemp()
    os.close(fd)
    removed = False
    with open(filename, "rb") as src, open(tmpname, "wb") as dst:
        while chunk := src.read(rec_size):
            if get_id_fn(chunk) == target_id:
                removed = True
                continue  # ข้ามเรคคอร์ดที่ต้องการลบ
            dst.write(chunk)
    if removed:
        os.replace(tmpname, filename)
    else:
        os.remove(tmpname)
    return removed

def delete_book(filename="books.dat"):
    try:
        target = int(input("Enter Book ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return
    ok = _rewrite_without_id(
        filename, BOOK_REC_SIZE,
        lambda c: int.from_bytes(c[0:4], "little"),
        target
    )
    print("Book deleted." if ok else "Book not found.")

def delete_member(filename="members.dat"):
    try:
        target = int(input("Enter Member ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return
    ok = _rewrite_without_id(
        filename, MEMB_REC_SIZE,
        lambda c: int.from_bytes(c[0:4], "little"),
        target
    )
    print("Member deleted." if ok else "Member not found.")
