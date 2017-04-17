
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn

def get_eta_table(): 
    eta_table_data = dict(
            ptype=['Hot Rock', 'Warm Rock', 'Cold Rock', 'Hot Neptunes', 'Warm Neptunes', 'Cold Neptunes','Hot Jupiters','Warm Jupiters','Cold Jupiters'], 
            radii=['0.5-1.4','0.5-1.4','0.5-1.4','1.4-4','1.4-4','1.4-4','4-11.6','4-11.6','4-11.6'], 
            eta=['0.82','0.41','0.41','0.69','0.35','0.35','0.09','0.09','0.09'], 
            a=['0.074-0.816','0.816-1.62','1.62-12.4','0.735-0.791','0.791-1.54','1.54-12.4','0.0735-0.803','0.803-1.58','1.58-13.5'] 
        )
    eta_table_source = ColumnDataSource(eta_table_data)
    eta_columns = [
            TableColumn(field="ptype", title="Planet Type"), 
            TableColumn(field="radii", title="R/R_Earth"),
            TableColumn(field="eta", title="Eta")] 

    return DataTable(source=eta_table_source, columns=eta_columns, width=450, height=980)




