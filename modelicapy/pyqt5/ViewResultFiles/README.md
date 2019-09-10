
## This is a simple demonstration of using pyqt5, leverage Qt Designer.


To run, convert the `.ui` and resource files. From the terminal:

```
pyuic5 forms\MainWindow.ui > generated\MainWindow.py
pyrcc5 icons\icons.qrc -o icons_rc.py
```

The gui should then be able to be views by running `main.py`

```
python main.py
```

To generate an executable:

```
pyinstaller main.spec
````

To test the gui, load `examplefile.mat` and enter `lorenzSystem.x` into the white space. Then click `Plot`.

## Notes:

- The first time pyinstaller is run on a `.py` file it generates a *.spec file. This file then instead be ran as above. This way the `.spec` file can be modified if necessary. In this example it had to be modified by adding the following lines of code at the top of the file:

```
import sys
sys.setrecursionlimit(5000)
```

- mplwidget.py: custom widget for plotting

## Requirements:

- python3 (via anaconda3)
- pyqt5
- buildingspy
- pyinstaller