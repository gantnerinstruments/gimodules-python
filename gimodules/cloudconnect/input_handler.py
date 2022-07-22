
import ipywidgets as widgets
from numpy import select  # import widgets for better user interaction
import datetime as dt
import numpy as np

# Letting the user choose a meas-period
"""
wid_meas=widgets.Dropdown(
    options=mess_start,
    value=mess_start[0],
    description='Measurement:',
    disabled=False,
)


stream_index = widgets.IntText(description='index:',value=0)
stream_ts_start = widgets.IntText(description='ts start:',value=measurement_list[0,0])
stream_ts_stop = widgets.IntText(description='ts stop:',value=measurement_list[len(measurement_list)-1,1])

wid_meas_end = widgets.Text(
    value=mess_end[0],
    placeholder='Paste ticket description here!',
    description='end:',
    #layout = widgets.Layout(width='400px'),
    disabled=False,
)

def meas_select_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        #print(str(wid_stream.value))
        stream_index.value=mess_start.index(wid_meas.value)
        wid_meas_end.value=mess_end[mess_start.index(wid_meas.value)]
        stream_ts_start.value=measurement_list[stream_index.value,0]
        stream_ts_stop.value=measurement_list[len(measurement_list)-1,1]
        display(stream_index,wid_meas,wid_meas_end,stream_ts_start,stream_ts_stop)
wid_meas.observe(meas_select_change,names='value')

display(wid_meas,wid_meas_end,stream_index,stream_ts_start,stream_ts_stop)

"""


class InputHandler():
    def __init__(self) -> None:
        pass

    def in_calc_measurements(self, sel_indices, channels):  # TODO rename function
        calculations = ("*", "/", "+", "-")
        temp = []
        self.sel_indices_map = {}
        counter = 0

        # Extract selected channel names
        for i in range(len(channels)):
            for j in range(len(sel_indices)):
                if (i == sel_indices[j]):
                    self.sel_indices_map.update({sel_indices[j]: counter})
                    counter += 1
                    temp.append(channels[i])

        self.sel_channel_1_widgets = [widgets.Dropdown(
            options=temp,
            description='Param_1:',
            disabled=False
        ) for chan in sel_indices]

        self.sel_calc_widgets = [widgets.Dropdown(
            options=calculations,
            description="Expression:",
            diabled=False
        ) for chan in sel_indices]

        self.sel_calc_2_widgets = [widgets.Dropdown(
            options=calculations,
            description="Expression:",
            diabled=False
        ) for chan in sel_indices]

        self.sel_param_widgets = [widgets.BoundedFloatText(
            value=1,
            description="Constant:",
            diabled=False
        ) for chan in sel_indices]

        temp2 = temp.copy()
        # As default, for ability to only use the constant
        temp2.insert(0, 'None')
        self.sel_channel_2_widgets = [widgets.Dropdown(
            options=temp2,
            description="Param_2:",
            disabled=False
        )for chan in sel_indices]

        self.sel_unit_widgets = [widgets.Text(
            description="Unit:",
            disabled=False
        ) for chan in sel_indices]

        # TODO place side by side
        # Display all widgets
        for i in range(len(self.sel_channel_1_widgets)):
            self.sel_channel_1_widgets[i].value = temp[i]
            display(self.sel_param_widgets[i], self.sel_calc_widgets[i], self.sel_channel_1_widgets[i],
                    self.sel_calc_2_widgets[i], self.sel_channel_2_widgets[i], self.sel_unit_widgets[i])

    def on_param_change(change):
        print()

    def in_calc_measurements_change(change):
        print()
        # if change['type'] == 'change' and change['name'] == 'value':

    def get_expr_param_for_sel_indices(self, sel_indices):
        if (not hasattr(self, "expr_param_map")):
            self.expr_param_map = {}
            """
            Expression map example: D = {'0': {'exp_c': '/', 'constant': '10', 'exp_2': '*' 'param_2': 'Gi_pyr'}} - 0 = channel/param_1
            """
        for i in range(len(sel_indices)):  # Not validated : could validate through map first
            self.expr_param_map.update(
                {i: {'param_1':self.sel_channel_1_widgets[i].value, 'exp_c': self.sel_calc_widgets[i].value, 'exp_2': self.sel_calc_2_widgets[i].value, 'constant': self.sel_param_widgets[i].value, 'param_2': self.sel_channel_2_widgets[i].value}})

        return self.expr_param_map
    
    def get_channel_name_by_index(widget, index):
        return widget.options[index]
    
    def get_channel_index_for_data(self, map_index, param, channel):
        if (channel == 1):
            return self.sel_channel_1_widgets[map_index].options.index(self.expr_param_map[map_index][param])
        elif (channel == 2):
            return self.sel_channel_2_widgets[map_index].options.index(self.expr_param_map[map_index][param])
    
    def declare_custom_units(self, sel_indices, unit_list):
        for i in range(len(sel_indices)):
            unit_list[sel_indices[i]] = self.sel_unit_widgets[i].value

    # above is mostly for python write
    #####################################################################
    def display_stream_channel_sel(self, conn_cloud, default_stream=0):
        """Displays different streams and lets user to pick different channels

        Args:
            conn_cloud (CloudRequest object): handles cloud requests (GQL requests)
            default_stream (int, optional): [description]. Defaults to 0.
        """
        if (default_stream != 0):
            default_stream = self.stream_list.index(default_stream)
        
        wid_stream=widgets.Dropdown(
            options=conn_cloud.stream_list,
            value=conn_cloud.stream_list[default_stream],
            description='Stream:',
            disabled=False,
        )

        stream_index = widgets.IntText()

        stream_ID_wid = widgets.Text(
            value=conn_cloud.stream_ID[default_stream],
            placeholder='Paste ticket description here!',
            description='Stream ID:',
            layout = widgets.Layout(width='400px'),
            disabled=True,
        )

        #map sources
        res=conn_cloud.variable_mapping(stream_ID_wid.value)
        index_var,name_var,unit_var,id_var=conn_cloud.get_var_mapping(conn_cloud.request_map_res)
        self.sel_stream_id = stream_ID_wid.value

        # We display interactively map sources
        self.wid_channel=widgets.SelectMultiple(
            options=name_var,
            #value=[name_var[3],name_var[8]], #preselected channels
            description='Channel:',
            layout = widgets.Layout(height='400px',width='400px'),
            disabled=False,
        )

        def dropdown_slect_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                self.wid_channel.disabled = True
                
                stream_index.value=conn_cloud.stream_list.index(wid_stream.value)
                stream_ID_wid.value=conn_cloud.stream_ID[stream_index.value]
                self.sel_stream_id = stream_ID_wid.value

                #we update the channels informations
                res=conn_cloud.variable_mapping(stream_ID_wid.value)
                index_var,name_var,unit_var,id_var=conn_cloud.get_var_mapping(conn_cloud.request_map_res)
                self.wid_channel.options=name_var
                #selected_index=[index_var[name_var.index(self.wid_channel.value[i])] for i in range(0,len(self.wid_channel.value))]
                #display the updated information selected_index=[index_var[name_var.index(wid_channel.value[i])] for i in range(0,len(wid_channel.value))]              
                self.wid_channel.disabled = False
                display(stream_index,conn_cloud.stream_IDD,self.wid_channel)
                
    
        wid_stream.observe(dropdown_slect_change,names='value')

        print("Choose the Stream and Variables of which you want to fetch data. \nPress CTRL to select multiple Variables.")
        display(wid_stream,stream_ID_wid,self.wid_channel)

    def get_selected_channel_indices(self, index_var, name_var):
        selected_index=[index_var[name_var.index(self.wid_channel.value[i])] for i in range(0,len(self.wid_channel.value))]
        return selected_index

    def display_date_pickers(self):
        """Display datepickers for data querying. Calculate timestamps on change of widget
        """
        # Create last week as default values
        today=dt.datetime.today()
        yesterday=dt.datetime.today() - dt.timedelta(days=1)
        a_week_ago=dt.datetime.today() - dt.timedelta(days=7)

        start_date_pick=widgets.DatePicker(
            value=a_week_ago,
            description='Start Date',
            disabled=False
        )

        end_date_pick=widgets.DatePicker(
            value=today,
            description='End Date',
            disabled=False
        )

        start_time_pick=widgets.Text(
            value='00:00:00',
            placeholder='Start time',
            description='String:',
            disabled=False
        )

        end_time_pick=widgets.Text(
            value='23:59:59',
            placeholder='Endtime',
            description='String:',
            disabled=False
        )
        
        

        def timedate_to_ts():
            time_start_obj = dt.datetime.strptime(start_time_pick.value,'%H:%M:%S').time()
            time_end_obj = dt.datetime.strptime(end_time_pick.value,'%H:%M:%S').time()
            start_day=dt.datetime.combine(start_date_pick.value,time_start_obj)
            end_day=dt.datetime.combine(end_date_pick.value,time_end_obj)
            self.timestamp_start = str(int(np.multiply(dt.datetime.timestamp(start_day),1000)))
            self.timestamp_stop = str(int(np.multiply(dt.datetime.timestamp(end_day),1000)))
            #print(self.timestamp_start + ' ' + self.timestamp_stop)

        

        out = widgets.Output() # To enable printing in same widget block
        display(out)
        
        @out.capture()
        def on_datetime_change(change):
            """On time or date change calculate these into new start/end timestamps

            Args:
                change (date/time is changed): 
            """
            if change['type'] == 'change' and change['name'] == 'value':
                timedate_to_ts()
        
        start_date_pick.observe(on_datetime_change, names='value')
        end_date_pick.observe(on_datetime_change, names='value')
        start_time_pick.observe(on_datetime_change, names='value')
        end_time_pick.observe(on_datetime_change, names='value')
        timedate_to_ts()
        display(start_date_pick,start_time_pick,end_date_pick,end_time_pick)

    def display_res_sel(self):
        self.wid_reso=widgets.Select(
            options=['MONTH','WEEK','DAY','HOUR','QUARTER_HOUR','MINUTE','SECOND','HZ10','HZ100','KHZ','KHZ10','nanos'],
            value='MINUTE',
            # rows=10,
            description='Resolution',
            disabled=False
        )
        display(self.wid_reso)

        self.sel_resolution = self.wid_reso.value

        def on_res_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                print(change)
                self.sel_resolution = change.new
        
        self.wid_reso.observe(on_res_change, names='value')