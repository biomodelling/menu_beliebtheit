# Menu Beliebtheit 
![PyPI](https://img.shields.io/pypi/v/menu-beliebtheits-rechner)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/menu-beliebtheits-rechner)
![GitHub](https://img.shields.io/github/license/biomodelling/menu_beliebtheit)

Berechnung der Beliebtheit von verschiedenen Menus basierend auf den Verkaufszahlen und Angebotskombinationen von verschiedenen Verkaufsstellen des Kanton Zürich (Spital, Kantine, etc.).

## Definition Beliebtheit
Die Beliebtheit eines Menus wird berechnet aus der Verkaufswahrscheinlichkeit abhängig von einem bestimmten Tagesangebot. Bspw. werden in einem Altersheim drei Menus basierend auf Quornschnitzel, Schnitzel-Pommes und Thaicurry angeboten, wird sich Schnitzel-Pommes wahrscheinlich am Besten verkaufen. Ändert sich das Angebot zu bspw. Hackbraten, Schnitzel-Pommes und Gulasch ist nicht mehr eindeutig zu erwarten, dass Schnitzel-Pommes sich am Besten verkaufen wird.

# Installation 
Clone the git repository
```
git clone https://github.com/biomodelling/menu_beliebtheit.git
```

Set up a virtual environement
```
$ cd ./menu_beliebtheit
$ python3 -m venv env
```

Step into the environment
```
$ source env/bin/activate
```

Install the requirements
```
$ pip3 -r REQUIREMENTS.TXT
```

# Usage
You can run the script with the command
```
python3 main.py -o <input/file> -n <output-filename-with-file-ending>
```

```-o / --output-format = file``` the script searches in ```menu_beliebtheit/data/``` for ```.csv``` files, sorts them alphabetically and keeps the first in the list as data source. This data source should represent selling data in the format

| date | meal_line | tot_sold | meal_component | meal_label | source |
|------|-----------|----------|----------------|------------|--------|
|2019-01-01|Vegi.Triemli|5|Quornschnitzel|vegetarian|triemli19|
|2019-01-01|Vegi.Triemli|5|Morchelsauce|vegetarian|triemli19|
|2019-01-01|Vegi.Triemli|5|Basmatireis|vegetarian|triemli19|
|2019-01-01|Vegi.Triemli|5|Salat|vegetarian|triemli19|
|2019-01-01|Tageshit.Triemli|30|Kalbssteak|meat|triemli19|
|2019-01-01 | Tageshit.Triemli | 30 | Morchelsauce | meat | triemli19 |
|2019-01-01 | Tageshit.Triemli | 30 | Griessgnocchi | meat | triemli19 |
|2019-01-01 | Tageshit.Triemli | 30 | Grune Bohnen | meat | triemli19 |
|2019-01-01 | Budget.Triemli | 15 | NA | NA | triemli19 |
|2019-01-02 | Vegi.Triemli | 15 | Gratinierte Spatzlipfanne mit | vegetarian | triemli19 |
|2019-01-02 | Vegi.Triemli | 15 | Karotten  Federkohl  | vegetarian | triemli19 |
|2019-01-02 | Vegi.Triemli | 15 | Lauch und Bergkase | vegetarian | triemli19 |
|2019-01-02 | Vegi.Triemli | 15 | Salat | vegetarian | triemli19 |


```-o / --output-format = input``` an input argument in a specified format must be provided (Development stage)

```-n / --file-name = popularity.csv``` allows to specify the filename and its ending where the popularity values are stored. It will be stored in the following format and sorted by the popularity index.

| meal_component | popularity |
|----------------|------------|
|appenzeller cordon bleu pommes frit salat| 0.018604 |
|kalbsbratwurst zwiebelsauc rosti salat | 0.010735 |
|zanderfilet bierteig remouladensauc petersilienkartoffeln salat | 0.009456 |
|kalbspiccata tomatensauc spaghetti salat | 0.008840 |
|zanderknusperli tartarsauc salzkartoffeln blattspinat | 0.008037 |
|ghackets rind hornli apfelmus salat | 0.007048 |