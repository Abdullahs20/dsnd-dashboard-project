from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent



class ReportDropdown(Dropdown):


    def build_component(self, entity_id, model):

        self.label = model.name
        

        return super().build_component(entity_id,model)

    

    def component_data(self, entity_id, model):
        return model.names()



class Header(BaseComponent):


    def build_component(self, entity_id, model):
        
        return H1(model.name)
        

          


class LineChart(MatplotlibViz):
    

    def visualization(self, asset_id, model):
        

        data = model.event_counts(asset_id)
        data = data.fillna(0).set_index('event_date').sort_index().cumsum()
        data.columns = ['Positive', 'Negative']
        fig, ax = plt.subplots()
        data.plot(ax=ax)
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
        ax.set_title('Cumulative Event Counts')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')

        
class BarChart(MatplotlibViz):


    predictor = load_model()

    def visualization(self, asset_id, model):
        data = model.model_data(asset_id)
        proba = self.predictor.predict_proba(data)
        proba = proba[:, 1]

        if model.name == 'team':
            pred = proba.mean()
        else:
            pred = proba[0]

        fig, ax = plt.subplots()

        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
   
class Visualizations(CombinedComponent):
    
    children = [LineChart(), BarChart()]

    children = [LineChart(), BarChart()]


    outer_div_type = Div(cls='grid')

class NotesTable(DataTable):


    def component_data(self, entity_id, model):
        return model.notes(entity_id)
        

    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    

class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


app = FastHTML()


report = Report()



@app.get("/")
def index():
    return report(1, Employee())



@app.get("/employee/{employee_id}")
def employee(employee_id:str):
    return report(employee_id, Employee())





@app.get("/team/{team_id}")
def team(team_id:str):
    return report(team_id, Team())
    




# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    


serve()
