from flask import Flask, render_template, request
from database import get_db, init_db, close_connection
import sqlite3

app = Flask(__name__)

# Initialize database
with app.app_context():
    init_db()

# Sample data for barnehager
barnehager = [
    {"barnehage_id": 1, "barnehage_navn": "Sunshine Preschool", "barnehage_antall_plasser": 50, "barnehage_ledige_plasser": 15},
    {"barnehage_id": 2, "barnehage_navn": "Happy Days Nursery", "barnehage_antall_plasser": 25, "barnehage_ledige_plasser": 2},
    {"barnehage_id": 3, "barnehage_navn": "123 Learning Center", "barnehage_antall_plasser": 35, "barnehage_ledige_plasser": 4},
    {"barnehage_id": 4, "barnehage_navn": "ABC Kindergarten", "barnehage_antall_plasser": 12, "barnehage_ledige_plasser": 0},
    {"barnehage_id": 5, "barnehage_navn": "Tiny Tots Academy", "barnehage_antall_plasser": 15, "barnehage_ledige_plasser": 5},
    {"barnehage_id": 6, "barnehage_navn": "Giggles and Grins Childcare", "barnehage_antall_plasser": 10, "barnehage_ledige_plasser": 0},
    {"barnehage_id": 7, "barnehage_navn": "Playful Pals Daycare", "barnehage_antall_plasser": 40, "barnehage_ledige_plasser": 6}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply')
def apply():
    return render_template('sok.html')

@app.route('/kindergartens')
def kindergartens():
    return render_template('barnehager.html', data=barnehager)

@app.route('/applications')
def applications():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT navn_forelder_1, prioriterte_barnehager, resultat, valgt_barnehage FROM soknader')

    soknader = []
    for row in cursor.fetchall():
        row_dict = dict(row)
        
        if 'prioriterte_barnehager' in row_dict and row_dict['prioriterte_barnehager']:
            row_dict['prioriterte_barnehager'] = row_dict['prioriterte_barnehager'].split(',')
        
        soknader.append(row_dict)
    return render_template('soknader.html', soknader=soknader)

@app.route('/behandle', methods=['POST'])
def behandle():
    # Gather data from the form submission
    navn_forelder_1 = request.form.get('navn_forelder_1')
    barnehage_prioritet_1 = request.form.get('barnehage_prioritet_1')
    barnehage_prioritet_2 = request.form.get('barnehage_prioritet_2')
    barnehage_prioritet_3 = request.form.get('barnehage_prioritet_3')

    fortrinnsrett_barnevern = request.form.get('fortrinnsrett_barnevern')
    fortrinnsrett_sykdom_familie = request.form.get('fortrinnsrett_sykdom_familie')
    fortrinnsrett_sykdom_barn = request.form.get('fortrinnsrett_sykdom_barn')

    # Check fortrinnsrett
    fortrinnsrett = any([fortrinnsrett_barnevern, fortrinnsrett_sykdom_familie, fortrinnsrett_sykdom_barn])

    # Handle barnehage prioritization and availability
    valgt_barnehage = None
    resultat = "AVSLAG"
    prioriteter = [barnehage_prioritet_1, barnehage_prioritet_2, barnehage_prioritet_3]

    for prioritet in prioriteter:
        for barnehage in barnehager:
            if barnehage["barnehage_navn"] == prioritet:
                if fortrinnsrett:
                    if barnehage["barnehage_ledige_plasser"] > 0:
                        valgt_barnehage = prioritet
                        barnehage["barnehage_ledige_plasser"] -= 1
                        resultat = "TILBUD"
                        break
                else:
                    if barnehage["barnehage_ledige_plasser"] > 3:
                        valgt_barnehage = prioritet
                        barnehage["barnehage_ledige_plasser"] -= 1
                        resultat = "TILBUD"
                        break
        if valgt_barnehage:
            break

    # Insert application data into the database
    db = get_db()
    db.execute('INSERT INTO soknader (navn_forelder_1, prioriterte_barnehager, resultat, valgt_barnehage) VALUES (?, ?, ?, ?)',
               (navn_forelder_1, ', '.join(prioriteter), resultat, valgt_barnehage))
    db.commit()

    # Prepare data for response
    data = {
        "resultat": resultat,
        "prioriteter": prioriteter,
        "valgt_barnehage": valgt_barnehage
    }
    return render_template('svar.html', data=data)

# Close database connection
app.teardown_appcontext(close_connection)

if __name__ == '__main__':
    app.run(debug=True)
