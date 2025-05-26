import pandas as pd
from io import StringIO

def csv2html(csv_string):
    # Read the csv file in
    csv_file = StringIO(csv_string)

    df = pd.read_csv(csv_file)


    # Assign to string
    htmTable = df.to_html()
    return htmTable

if __name__ == "__main__":

    the_data = [
        "eFormat, Description",
        "E-Book, 'Kindle or Apple books - etc'",
        "PDF, formatted for printing and direct delivery",
    ]
    
    the_input = "\n".join(the_data)


    print("\n", the_input)
    html = csv2html(the_input)
    print("\nThe result")

    print(html)
