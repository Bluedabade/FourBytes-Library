import os
from datetime import datetime
from module.utils import from_i32, from_str

BOOK_REC_SIZE   = 88
MEM_REC_SIZE    = 92
BORROW_REC_SIZE = 36

def _load_books(path="storage/books.dat"):
    books = {}
    try:
        with open(path, "rb") as f:
            while chunk := f.read(BOOK_REC_SIZE):
                if from_i32(chunk[84:88]) != 0:  
                    continue
                book_id = from_i32(chunk[0:4])
                title   = from_str(chunk[4:24])
                books[book_id] = title
    except FileNotFoundError:
        pass
    return books

def _load_members(path="storage/members.dat"):
    members = {}
    try:
        with open(path, "rb") as f:
            while chunk := f.read(MEM_REC_SIZE):
                if from_i32(chunk[88:92]) != 0:  
                    continue
                member_id = from_i32(chunk[0:4])
                name      = from_str(chunk[4:24])
                phone     = from_str(chunk[44:54])
                members[member_id] = (name, phone)
    except FileNotFoundError:
        pass
    return members

def _load_borrows(path="storage/borrows.dat"):
    records = []
    try:
        with open(path, "rb") as f:
            while chunk := f.read(BORROW_REC_SIZE):
                records.append({
                    "borrow_id":   from_i32(chunk[0:4]),
                    "member_id":   from_i32(chunk[4:8]),
                    "book_id":     from_i32(chunk[8:12]),
                    "borrow_date": from_str(chunk[12:20]),
                    "due_date":    from_str(chunk[20:28]),
                    "return_date": from_str(chunk[28:36]),
                })
    except FileNotFoundError:
        pass
    return records

def _line(n=100, ch="-"):
    return ch * n + "\n"

def _fmt_date8(yyyymmdd: str) -> str:
    if yyyymmdd == "00000000" or len(yyyymmdd) != 8 or not yyyymmdd.isdigit():
        return "-"
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"

def generate_report():
    if not os.path.exists("report"):
        os.makedirs("report")

    ts = datetime.now()
    filename = f"report/report_{ts.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    books   = _load_books()
    members = _load_members()
    borrows = _load_borrows()

    total_borrows   = len(borrows)
    active_borrows  = sum(1 for r in borrows if r["return_date"] == "00000000")
    returned_borrows= total_borrows - active_borrows

    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*100 + "\n")
        f.write("  LIBRARY MANAGEMENT SYSTEM - BORROW/RETURN SUMMARY REPORT\n")
        f.write("="*100 + "\n")
        f.write(f"Generated At : {ts.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Encoding     : UTF-8\n")
        f.write("Content      : Borrow/Return summary only\n")
        f.write(_line(100))

        f.write("BORROW/RETURN RECORDS\n")
        f.write(_line(100))
        f.write(f"{'BorrowID':<9} {'MemberID':<8} {'Member Name':<20} {'Phone':<12} "
                f"{'BookID':<7} {'Book Title':<20} {'Borrow':<10} {'Due':<10} {'Return':<10} {'Status':<8}\n")
        f.write(_line(100))

        if not borrows:
            f.write("(no borrow records)\n")
        else:
            for r in borrows:
                mid = r["member_id"]
                bid = r["book_id"]

                name, phone = members.get(mid, ("(unknown)", "-"))
                title       = books.get(bid, "(unknown)")

                status = "Active" if r["return_date"] == "00000000" else "Returned"
                bdate  = _fmt_date8(r["borrow_date"])
                ddate  = _fmt_date8(r["due_date"])
                rdate  = _fmt_date8(r["return_date"])

                f.write(f"{r['borrow_id']:<9} {mid:<8} {name:<20} {phone:<12} "
                        f"{bid:<7} {title:<20} {bdate:<10} {ddate:<10} {rdate:<10} {status:<8}\n")

        f.write("\n" + _line(100))
        f.write("SUMMARY\n")
        f.write(_line(100))
        f.write(f"- Total Borrow Records : {total_borrows}\n")
        f.write(f"- Currently Borrowed   : {active_borrows}\n")
        f.write(f"- Returned             : {returned_borrows}\n")
        f.write("="*100 + "\n")

    print(f"Report generated: {filename}")
