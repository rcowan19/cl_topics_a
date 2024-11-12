import csv

dates = []

class Date:
    def __init__(self, month, day, blocklist, weekday, term):
        self.month = month
        self.day = day
        self.blocklist = blocklist
        self.weekday = weekday
        self.term = term

    def __repr__(self):
        return f"Month:{self.month} Day:{self.day} BlockList:{self.blocklist} Weekday:{self.weekday} Term:{self.term}"

def to_dict(dates):
    term_dict = {}
    for date in dates:
        
        if date.term not in term_dict:
            term_dict[date.term] = {}
        term_dates = term_dict[date.term]

        key = f"{date.month}-{date.day}"
        if key not in term_dates:
            term_dates[key] = []

        info = [date.blocklist, date.weekday]
        term_dates[key].append(info)
    return term_dict

def read_dates():
    with open("classes.csv", 'r', encoding="utf-8-sig") as file:
        reader_dict = csv.DictReader(file)
        term = None  
        for row in reader_dict:
            if row["term"] in ["FALL TERM", "WINTER TERM", "SPRING TERM"]:
                term = row["term"]
            else:
                continue  

            calendar_day = row["calendar_day"]
            block_list = create_blocklist(row["d_label"])
            weekday = row["weekday"]
            if not calendar_day or not block_list or not weekday:
                continue

           
            month, day = calendar_day.split("-")
            dates.append(Date(month, day, block_list, weekday, term))

def create_blocklist(day):
    block_list = []
    if len(day) > 1 and day[1:].isdigit():
        day_num = int(day[1:])
        for i in range(4):
            block_num = ((day_num + i - 1) % 7) + 1
            block_list.append(f"B{block_num}")
    return block_list

read_dates()
term_dict = to_dict(dates)
print(term_dict)
