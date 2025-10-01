import os
from datetime import datetime
from module.utils import from_i32, from_str

BOOK_REC_SIZE   = 88   
MEM_REC_SIZE    = 92   
BORROW_REC_SIZE = 36   

def _line(n=60, ch="-"):
    return ch * n + "\n"

def _fmt_row(cols, widths):
    return " ".join(f"{str(val):<{w}}" for val, w in zip(cols, widths)) + "\n"

def _read_books(path="storage/books.dat"):
    """Yield (active_only) and also return totals for counts."""
    books = []
    total_count = 0
    deleted_count = 0
    try:
        with open(path, "rb") as f:
            while chunk := f.read(BOOK_REC_SIZE):
                total_count += 1
                deleted = from_i32(chunk[84:88])
                if deleted != 0:
                    deleted_count += 1
                    continue
                rec = {
                    "book_id":   from_i32(chunk[0:4]),
                    "title":     from_str(chunk[4:24]),
                    "author":    from_str(chunk[24:44]),
                    "publisher": from_str(chunk[44:64]),
                    "year":      from_i32(chunk[64:68]),
                    "total":     from_i32(chunk[68:72]),
                    "avail":     from_i32(chunk[72:76]),
                    "price":     from_str(chunk[76:84]),
                }
                books.append(rec)
    except FileNotFoundError:
        pass
    return books, total_count, deleted_count

def _read_members(path="storage/members.dat"):
    members = []
    total_count = 0
    deleted_count = 0
    try:
        with open(path, "rb") as f:
            while chunk := f.read(MEM_REC_SIZE):
                total_count += 1
                deleted = from_i32(chunk[88:92])
                if deleted != 0:
                    deleted_count += 1
                    continue
                rec = {
                    "member_id": from_i32(chunk[0:4]),
                    "full_name": from_str(chunk[4:24]),
                    "address":   from_str(chunk[24:44]),
                    "phone":     from_str(chunk[44:54]),
                    "email":     from_str(chunk[54:84]),
                    "join_year": from_i32(chunk[84:88]),
                }
                members.append(rec)
    except FileNotFoundError:
        pass
    return members, total_count, deleted_count

def _read_borrows(path="storage/borrows.dat"):
    borrows = []
    try:
        with open(path, "rb") as f:
            while chunk := f.read(BORROW_REC_SIZE):
                rec = {
                    "borrow_id":   from_i32(chunk[0:4]),
                    "member_id":   from_i32(chunk[4:8]),
                    "book_id":     from_i32(chunk[8:12]),
                    "borrow_date": from_str(chunk[12:20]),
                    "due_date":    from_str(chunk[20:28]),
                    "return_date": from_str(chunk[28:36]),
                }
                borrows.append(rec)
    except FileNotFoundError:
        pass
    return borrows

# ---- Aggregations ----
def _summarize_books(books):
    total_titles   = len(books)
    sum_total      = sum(b["total"] for b in books) if books else 0
    sum_available  = sum(b["avail"] for b in books) if books else 0
    return total_titles, sum_total, sum_available

def _summarize_borrows(borrows):
    total_records   = len(borrows)
    active_borrows  = sum(1 for r in borrows if r["return_date"] == "00000000")
    returned        = total_records - active_borrows
    return total_records, active_borrows, returned

def _active_borrows_by_member(borrows):
    """Return dict member_id -> count of active borrows"""
    d = {}
    for r in borrows:
        if r["return_date"] == "00000000":
            mid = r["member_id"]
            d[mid] = d.get(mid, 0) + 1
    return d

def _active_borrows_by_book(borrows):
    """Return dict book_id -> count of active borrows"""
    d = {}
    for r in borrows:
        if r["return_date"] == "00000000":
            bid = r["book_id"]
            d[bid] = d.get(bid, 0) + 1
    return d

def generate_report():
    if not os.path.exists("report"):
        os.makedirs("report")

    ts = datetime.now()
    filename = f"report/report_{ts.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    books, books_total, books_deleted = _read_books()
    members, members_total, members_deleted = _read_members()
    borrows = _read_borrows()

    total_titles, sum_total, sum_available = _summarize_books(books)
    bor_total, bor_active, bor_returned   = _summarize_borrows(borrows)
    active_by_member = _active_borrows_by_member(borrows)
    active_by_book   = _active_borrows_by_book(borrows)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("  LIBRARY MANAGEMENT SYSTEM - SUMMARY REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Generated At : {ts.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Encoding     : UTF-8\n")
        f.write("Data Type    : int / float / string (fixed length)\n")
        f.write(_line(60))

        f.write("BOOKS (Active)\n")
        f.write(_line(60))
        f.write(_fmt_row(
            ["ID", "Title", "Author", "Publisher", "Year", "Total", "Avail", "Price"],
            [5, 20, 20, 20, 6, 6, 6, 8]
        ))
        f.write(_line(60))
        if books:
            for b in books:
                f.write(_fmt_row(
                    [b["book_id"], b["title"], b["author"], b["publisher"], b["year"], b["total"], b["avail"], b["price"]],
                    [5, 20, 20, 20, 6, 6, 6, 8]
                ))
        else:
            f.write("(no active books)\n")
        f.write("\n")
        f.write(f"Total Book Records : {books_total}\n")
        f.write(f"Active Books       : {len(books)}\n")
        f.write(f"Deleted Books      : {books_deleted}\n")
        f.write(f"Total Copies       : {sum_total}\n")
        f.write(f"Available Copies   : {sum_available}\n")
        f.write(_line(60))
        f.write("\n")

        f.write("MEMBERS (Active)\n")
        f.write(_line(60))
        f.write(_fmt_row(
            ["ID", "Full Name", "Address", "Phone", "Email", "Year"],
            [5, 20, 20, 12, 30, 6]
        ))
        f.write(_line(60))
        if members:
            for m in members:
                f.write(_fmt_row(
                    [m["member_id"], m["full_name"], m["address"], m["phone"], m["email"], m["join_year"]],
                    [5, 20, 20, 12, 30, 6]
                ))
        else:
            f.write("(no active members)\n")
        f.write("\n")
        f.write(f"Total Member Records : {members_total}\n")
        f.write(f"Active Members       : {len(members)}\n")
        f.write(f"Deleted Members      : {members_deleted}\n")
        f.write(_line(60))
        f.write("\n")

        f.write("BORROWS (All)\n")
        f.write(_line(60))
        f.write(_fmt_row(
            ["BorrowID", "MemberID", "BookID", "BorrowDate", "DueDate", "ReturnDate", "Status"],
            [9, 8, 8, 10, 10, 10, 8]
        ))
        f.write(_line(60))
        if borrows:
            for r in borrows:
                status = "Active" if r["return_date"] == "00000000" else "Returned"
                f.write(_fmt_row(
                    [r["borrow_id"], r["member_id"], r["book_id"], r["borrow_date"], r["due_date"], r["return_date"], status],
                    [9, 8, 8, 10, 10, 10, 8]
                ))
        else:
            f.write("(no borrow records)\n")
        f.write("\n")
        f.write(f"Total Borrow Records : {bor_total}\n")
        f.write(f"Currently Borrowed   : {bor_active}\n")
        f.write(f"Returned             : {bor_returned}\n")
        f.write(_line(60))
        f.write("\n")

        f.write("SUMMARY\n")
        f.write(_line(60))
        f.write(f"- Active Books            : {len(books)}\n")
        f.write(f"- Active Members          : {len(members)}\n")
        f.write(f"- Books Currently Borrowed: {bor_active}\n")
        f.write(f"- Copies Available        : {sum_available}\n")
        f.write("\n")

        if bor_active > 0:
            if active_by_member:
                f.write("Active Borrows by Member (member_id: count)\n")
                f.write(_line(60))
                for mid, cnt in sorted(active_by_member.items(), key=lambda x: (-x[1], x[0])):
                    f.write(f"{mid}: {cnt}\n")
                f.write("\n")

            if active_by_book:
                f.write("Active Borrows by Book (book_id: count)\n")
                f.write(_line(60))
                for bid, cnt in sorted(active_by_book.items(), key=lambda x: (-x[1], x[0])):
                    f.write(f"{bid}: {cnt}\n")
                f.write("\n")

        f.write("="*60 + "\n")

    print(f"Report generated: {filename}")
