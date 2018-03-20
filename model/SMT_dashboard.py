# GUI Front-end for the SMT_simulator
# built using Kivy (https://kivy.org/#home)

# Author: Neha Karanjkar


# Kivy-related imports:
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label  import Label
from kivy.uix.button  import Button
from kivy.uix.splitter import Splitter
from kivy.uix.textinput  import TextInput
from kivy.uix.image  import Image
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle

# Simulator-related
import SMT_simulation


#A TextInput widget that allows only numbers(integers)
#to be entered.
class IntegerInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        s=""
        try:
            num = int(substring)
            s=str(num)
        except ValueError as verr:
            num = 0
            s=""
        return super(IntegerInput, self).insert_text(str(s), from_undo=from_undo)

class ScrollLabel(ScrollView):
    text = ""
    pass

class ParameterSetupGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(ParameterSetupGridLayout, self).__init__(**kwargs)
        self.cols=2
        self.padding=5
        self.spacing=5
        #for i in [1,2,3]:
        #    self.add_widget(Label(text="Foo"))


Builder.load_string("""
<DashboardTabs>:

    do_default_tab: False
    TabbedPanelItem:
        text: 'Overview'
        GridLayout:
            rows:2
            spacing:10
            padding:10
            Label:
                text: 'The SMT line Model'
                size_hint_y:None
                height:20
            Image:
                source:"SMT_line.png"
                keep_ratio:True
    TabbedPanelItem:
        text: 'Parameters'
        GridLayout:
            rows:8
            spacing:10
            padding:10
            Label:
                text: 'Set model parameters:'
                size_hint_y:None
                height:40
            
            ParameterSetupGridLayout:
                
                Label:
                    text: 'Screen printer latency (seconds):'
                IntegerInput:
                    id: param_screen_printer_latency
                    multiline:False
                    input_type:'number'
                    text:str(app.param_screen_printer_latency_default)
                
                Label:
                    text: 'Pick_and_place_1 latency (seconds):'
                IntegerInput:
                    id: param_pick_and_place_1_latency
                    multiline:False
                    input_type:'number'
                    text:str(app.param_pick_and_place_1_latency_default)
                
                Label:
                    text: 'Pick_and_place_2 latency (seconds):'
                IntegerInput:
                    id: param_pick_and_place_2_latency
                    multiline:False
                    input_type:'number'
                    text:str(app.param_pick_and_place_2_latency_default)
            Button:
                text: 'Set'
                on_press:root.set_parameters()
                size_hint_y:None
                height:40

    TabbedPanelItem:
        text: 'Simulation'
        GridLayout:
            rows:5
            row_force_default:False
            spacing:10
            padding:10

            Label:
                text: 'Run Simulation'
                size_hint_y:None
                height:40
            
            GridLayout:
                height: 60
                cols:3
                spacing:5
                padding:5
                size_hint_y:None
                height:60
                
                Label:
                    text: 'Enter simulation time (in seconds):'
                IntegerInput:
                    id: param_simulation_time
                    multiline:False
                    input_type:'number'
                    text:str(app.param_simulation_time_default)
                Button:
                    text: 'Run Simulation'
                    on_press:root.run_simulation()
            Splitter:
                sizable_from: 'top'
                ScrollLabel:
                    text: 'Simulation Results'
                    Label:
                        id: id_label_simulation_results
                        text: "\\nSimulation Results:"
                        font_size: 15
                        text_size: None, None           
                        size_hint_y: None
                        height: self.texture_size[1]
                        size_hint_x: None
                        width: self.texture_size[0]
    TabbedPanelItem:
        text: 'Activity Log'
        ScrollLabel:
            text: "Label1"
            Label:
                id: id_label_activity_log
                text: "<empty>"
                font_size: 15
                text_size: self.width, None           
                size_hint_y: None
                height: self.texture_size[1]
""")

from io import StringIO

class DashboardTabs(TabbedPanel):
    def set_parameters(self):
        param_screen_printer_latency = int(self.ids.param_screen_printer_latency.text)
        param_pick_and_place_1_latency = int(self.ids.param_pick_and_place_1_latency.text)
        param_pick_and_place_2_latency = int(self.ids.param_pick_and_place_2_latency.text)

        print(param_screen_printer_latency)

    def run_simulation(self):
        # run simulation
        simulation_time = int(self.ids.param_simulation_time.text)
        assert(simulation_time>=1 and simulation_time<1e10)
        param_values = {"foo":0}
        results_string = SMT_simulation.run_SMT_simulation(simulation_time, param_values)
        
        #obtain and print the activity log
        with open("activity_log.txt") as f:
            log = f.read()
            self.ids.id_label_activity_log.text = log

        #print aggregate results 
        self.ids.id_label_simulation_results.text="\nSimulation Results:\n"+ results_string.getvalue()
        pass
    pass


class SMT_simulatorApp(App):

    #default parameter values:
    param_screen_printer_latency_default=10
    param_pick_and_place_1_latency_default=10
    param_pick_and_place_2_latency_default=10
    param_simulation_time_default=100

    def build(self):
        return DashboardTabs()


if __name__ == '__main__':
    SMT_simulatorApp().run()
