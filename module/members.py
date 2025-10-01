from module.utils import fix_str, from_str, to_i32, from_i32

MEM_REC_SIZE = 92  

def _scan_max_id(filename):
    max_id = 0
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(MEM_REC_SIZE):
                mid = from_i32(chunk[0:4])
                if mid > max_id:
                    max_id = mid
    except FileNotFoundError:
        pass
    return max_id

def get_next_member_id(filename="storage/members.dat"):
    return _scan_max_id(filename) + 1

def _find_record_pos_by_id(target_id, filename):
    try:
        with open(filename, "rb") as f:
            pos = 0
            while chunk := f.read(MEM_REC_SIZE):
                mid = from_i32(chunk[0:4])
                if mid == target_id:
                    return pos, chunk
                pos += MEM_REC_SIZE
    except FileNotFoundError:
        return -1, None
    return -1, None

def add_member(filename="storage/members.dat"):
    member_id = get_next_member_id(filename)
    print(f"Assigned Member ID: {member_id}")

    while True:
        year_str = input("Enter Join Year: ").strip()
        if year_str.isdigit() and int(year_str) > 0:
            join_year = int(year_str)
            break
        print("Invalid join year. Please enter a positive number.")

    while True:
        full_name = input("Enter Full Name: ").strip()
        if full_name:
            break
        print("Full name cannot be empty.")

    while True:
        address = input("Enter Address: ").strip()
        if address:
            break
        print("Address cannot be empty.")

    while True:
        phone = input("Enter Phone (10 digits): ").strip()
        if phone.isdigit() and 7 <= len(phone) <= 10:
            break
        print("Invalid phone number. Must be digits, 7–10 characters.")

    while True:
        email = input("Enter Email: ").strip()
        if "@" in email and "." in email and len(email) > 5:
            break
        print("Invalid email address.")

    record = (
        to_i32(member_id) +
        fix_str(full_name, 20) +
        fix_str(address, 20) +
        fix_str(phone, 10) +
        fix_str(email, 30) +
        to_i32(join_year) +
        to_i32(0)  
    )
    with open(filename, "ab") as f:
        f.write(record)
    print("Member added successfully.")


def view_members(filename="storage/members.dat"):
    try:
        with open(filename, "rb") as f:
            print(f"{'ID':<5} {'Full Name':<20} {'Address':<20} {'Phone':<12} {'Email':<30} {'Year':<6}")
            print("-"*95)
            found = False
            while chunk := f.read(MEM_REC_SIZE):
                deleted = from_i32(chunk[88:92])
                if deleted != 0:
                    continue
                member_id = from_i32(chunk[0:4])
                full_name = from_str(chunk[4:24])
                address   = from_str(chunk[24:44])
                phone     = from_str(chunk[44:54])
                email     = from_str(chunk[54:84])
                join_year = from_i32(chunk[84:88])
                print(f"{member_id:<5} {full_name:<20} {address:<20} {phone:<12} {email:<30} {join_year:<6}")
                found = True
            if not found:
                print("No active member records found.")
    except FileNotFoundError:
        print("No member records found.")


def update_member(filename="storage/members.dat"):
    try:
        target_id = int(input("Enter Member ID to update: ").strip())
    except ValueError:
        print("Invalid Member ID.")
        return

    pos, chunk = _find_record_pos_by_id(target_id, filename)
    if pos < 0 or chunk is None or from_i32(chunk[88:92]) != 0:
        print("Member not found.")
        return

    print("Leave blank to keep old value.")
    with open(filename, "r+b") as f:
        new_name = input("New Full Name: ").strip()
        if new_name:
            f.seek(pos + 4); f.write(fix_str(new_name, 20))

        new_addr = input("New Address: ").strip()
        if new_addr:
            f.seek(pos + 24); f.write(fix_str(new_addr, 20))

        while True:
            new_phone = input("New Phone: ").strip()
            if not new_phone:
                break
            if new_phone.isdigit() and 7 <= len(new_phone) <= 10:
                f.seek(pos + 44); f.write(fix_str(new_phone, 10))
                break
            print("Invalid phone. Must be digits, 7–10 characters or leave blank.")

        while True:
            new_email = input("New Email: ").strip()
            if not new_email:
                break
            if "@" in new_email and "." in new_email and len(new_email) > 5:
                f.seek(pos + 54); f.write(fix_str(new_email, 30))
                break
            print("Invalid email. Try again or leave blank.")

        while True:
            new_year = input("New Join Year: ").strip()
            if not new_year:
                break
            if new_year.isdigit() and int(new_year) > 0:
                f.seek(pos + 84); f.write(to_i32(int(new_year)))
                break
            print("Invalid join year. Must be a positive number or leave blank.")

    print("Member updated successfully.")


def delete_member(filename="storage/members.dat"):
    try:
        target_id = int(input("Enter Member ID to delete: ").strip())
    except ValueError:
        print("Invalid Member ID.")
        return

    pos, chunk = _find_record_pos_by_id(target_id, filename)
    if pos < 0 or chunk is None:
        print("Member not found.")
        return

    confirm = input(f"Are you sure you want to delete Member ID {target_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        with open(filename, "r+b") as f:
            f.seek(pos + 88)
            f.write(to_i32(1))
        print("Member deleted successfully.")
    except FileNotFoundError:
        print("No member records found.")

def member_exists_and_active(member_id, filename="storage/members.dat"):
    pos, chunk = _find_record_pos_by_id(member_id, filename)
    if pos < 0 or chunk is None:
        return False
    return from_i32(chunk[88:92]) == 0
