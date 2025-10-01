from module.utils import fix_str, from_str, to_i32, from_i32
from module.books import book_exists_and_active, get_book_avail, set_book_avail_at_pos
from module.members import member_exists_and_active

BORROW_REC_SIZE = 36

def _scan_max_id(filename="storage/borrows.dat"):
    max_id = 0
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(BORROW_REC_SIZE):
                bid = from_i32(chunk[0:4])
                if bid > max_id:
                    max_id = bid
    except FileNotFoundError:
        pass
    return max_id

def get_next_borrow_id(filename="storage/borrows.dat"):
    return _scan_max_id(filename) + 1

def _find_record_pos_by_id(target_id, filename="storage/borrows.dat"):
    try:
        with open(filename, "rb") as f:
            pos = 0
            while chunk := f.read(BORROW_REC_SIZE):
                borid = from_i32(chunk[0:4])
                if borid == target_id:
                    return pos, chunk
                pos += BORROW_REC_SIZE
    except FileNotFoundError:
        return -1, None
    return -1, None

def _valid_date8(s):
    return len(s) == 8 and s.isdigit()

def _is_leap(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def _days_in_month(month: int, year: int) -> int:
    if month in (1,3,5,7,8,10,12):
        return 31
    if month in (4,6,9,11):
        return 30
    return 29 if _is_leap(year) else 28

def _input_int_in_range(prompt: str, lo: int, hi: int) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            v = int(s)
            if lo <= v <= hi:
                return v
        print(f"Invalid input. Please enter an integer in range {lo}-{hi}.")

def _input_date_yyyymmdd(prefix: str) -> str:
    while True:
        d = _input_int_in_range(f"{prefix} Day (1-31): ", 1, 31)
        m = _input_int_in_range(f"{prefix} Month (1-12): ", 1, 12)
        y = _input_int_in_range(f"{prefix} Year (e.g., 2025): ", 1, 9999)
        if d <= _days_in_month(m, y):
            return f"{y:04d}{m:02d}{d:02d}"
        print("Invalid date for that month/year. Please try again.")

def _active_duplicate_exists(member_id: int, book_id: int, filename="storage/borrows.dat") -> bool:
    """Return True if this member currently borrows the same book and has not returned it yet."""
    try:
        with open(filename, "rb") as f:
            while chunk := f.read(BORROW_REC_SIZE):
                mid = from_i32(chunk[4:8])
                bid = from_i32(chunk[8:12])
                ret = from_str(chunk[28:36])
                if mid == member_id and bid == book_id and ret == "00000000":
                    return True
    except FileNotFoundError:
        pass
    return False

def add_borrow(filename="storage/borrows.dat"):
    borrow_id = get_next_borrow_id(filename)
    print(f"Assigned Borrow ID: {borrow_id}")

    while True:
        mid = input("Enter Member ID: ").strip()
        if mid.isdigit():
            member_id = int(mid)
            if member_exists_and_active(member_id):
                break
            else:
                print("Member does not exist or has been deleted.")
        else:
            print("Invalid Member ID. Must be digits.")

    while True:
        bid = input("Enter Book ID: ").strip()
        if bid.isdigit():
            book_id = int(bid)
            if book_exists_and_active(book_id):
                break
            else:
                print("Book does not exist or has been deleted.")
        else:
            print("Invalid Book ID. Must be digits.")

    if _active_duplicate_exists(member_id, book_id, filename):
        print("This member already has this book borrowed and not yet returned.")
        return

    borrow_date = _input_date_yyyymmdd("Borrow")

    while True:
        due_date = _input_date_yyyymmdd("Due")
        if due_date >= borrow_date:
            break
        print("Due date cannot be earlier than borrow date.")

    bpos, total, avail = get_book_avail(book_id)
    if avail <= 0:
        print("No available copies for this book.")
        return

    record = (
        to_i32(borrow_id) +
        to_i32(member_id) +
        to_i32(book_id) +
        fix_str(borrow_date, 8) +
        fix_str(due_date, 8) +
        fix_str("00000000", 8)
    )
    with open(filename, "ab") as f:
        f.write(record)

    set_book_avail_at_pos(bpos, avail - 1)
    print("Borrow record added successfully.")

def return_book(filename="storage/borrows.dat"):
    while True:
        target = input("Enter Borrow ID to return: ").strip()
        if target.isdigit():
            target_id = int(target)
            break
        print("Invalid Borrow ID. Must be digits.")

    pos, chunk = _find_record_pos_by_id(target_id, filename)
    if pos < 0 or chunk is None:
        print("Borrow record not found.")
        return

    cur_return = from_str(chunk[28:36])
    if cur_return != "00000000":
        print("This borrow has already been returned.")
        return

    while True:
        return_date = _input_date_yyyymmdd("Return")
        borrow_date = from_str(chunk[12:20])
        if return_date >= borrow_date:
            break
        print("Return date cannot be earlier than borrow date.")

    confirm = input(f"Are you sure you want to return Borrow ID {target_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Return cancelled.")
        return

    book_id = from_i32(chunk[8:12])
    bpos, total, avail = get_book_avail(book_id)
    if bpos >= 0:
        set_book_avail_at_pos(bpos, avail + 1)

    with open(filename, "r+b") as f:
        f.seek(pos + 28)
        f.write(fix_str(return_date, 8))

    print("Book returned successfully.")

def view_borrows(filename="storage/borrows.dat"):
    try:
        with open(filename, "rb") as f:
            print(f"{'BorrowID':<8} {'MemberID':<8} {'BookID':<8} {'BorrowDate':<10} {'DueDate':<10} {'ReturnDate':<10}")
            print("-"*60)
            found = False
            while chunk := f.read(BORROW_REC_SIZE):
                borrow_id   = from_i32(chunk[0:4])
                member_id   = from_i32(chunk[4:8])
                book_id     = from_i32(chunk[8:12])
                borrow_date = from_str(chunk[12:20])
                due_date    = from_str(chunk[20:28])
                return_date = from_str(chunk[28:36])
                print(f"{borrow_id:<8} {member_id:<8} {book_id:<8} {borrow_date:<10} {due_date:<10} {return_date:<10}")
                found = True
            if not found:
                print("No borrow records found.")
    except FileNotFoundError:
        print("No borrow records found.")
