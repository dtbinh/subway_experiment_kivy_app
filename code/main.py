#Issues:
#1. Run on a device to update for better fontsizes.
from kivy.storage.jsonstore import JsonStore
from os.path import join
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from datetime import datetime
from kivy.uix.filechooser import FileSystemLocal
from kivy.clock import Clock,mainthread
from  kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from  kivy.metrics import sp
import re,os,string
import dropbox
import threading
from kivy.garden.scrolllabel import ScrollLabel
#Other functionality
username=''
class Experiment_Data():
	def update_filename(self,name,path):
		self.exp_file_name=name
		self.exp_file_path=path
	def update_exp_data(self,num_of_exit_ppl,num_of_steps,time_to_exit,date,time,centre):
		self.num_of_exit_ppl=num_of_exit_ppl
		self.num_of_steps=num_of_steps
		self.time_to_exit=time_to_exit
		self.date=date
		self.time=time
		self.centre=centre
	def update_location_valid(self,valid,location):
		self.valid=valid
		self.location=location    
	def print_data(self):
		print self.username,"__"
	def write_data(self):
		with open(self.exp_file_path,'a')as csvfile:
			data=[str(self.num_of_steps),self.centre,str(self.time_to_exit),str(self.num_of_exit_ppl),
				str(self.date),str(self.time),self.location,self.valid,self.username]
			csvfile.write (','.join(data)+'\n')
			print self.username,"___"
		save_popup=Popup(title='Confirmation',content=Label(text="Data added to Experiment:\n"+"'"+self.exp_file_name[:-4]+"'"+\
			".\n Saved at\n"+self.exp_file_path),size_hint=(1,.50),auto_dismiss=True)
		save_popup.open()
		Clock.schedule_interval(save_popup.dismiss, 3)
	def clear_object(self):
		self.exp_file_name='';self.exp_file_path='';self.num_of_exit_ppl='';
		self.num_of_steps='';self.time_to_exit='';self.date='';self.time='';
		self.valid='';self.location=''
	def set_username(self,username):
		self.username=username
#All screens

class LoginScreen(Screen):
	store=''
	username=''
	def __init__(self,**kwargs):
		super(LoginScreen, self).__init__(**kwargs)
		Clock.schedule_once(self.update_layout,1/60)
	def update_layout(self,btn):           
		data_dir= App.get_running_app().user_data_dir+'/'
		self.store = JsonStore(join(data_dir, 'storage.json'))       
		try:    
			self.username=self.store.get('credentials')['username']
			exp_data.set_username(self.username)
			self.parent.current = 'ExperimentSelectScreen'
		except KeyError:
			box=BoxLayout(orientation= 'vertical',padding=(100,100,100,100))
			#l=Label(size_hint_y=0.25)
			#box.add_widget(l)
			box.add_widget(Label(text="Enter email",font_size= sp(30),size_hint_y=.5))
			self.t=TextInput(font_size= sp(30),size_hint_y=0.5)
			box.add_widget(self.t)
			box.add_widget(Button(text="Okay",on_press=self.change_screen,font_size=sp(25),size_hint_y=.25))
			#box.add_widget(l)
			self.add_widget(box)


		#     #AppScreen.store.put('credentials', username=username, password=password)
	def change_screen(self,btn):
		if len(self.t.text) == 0:         #deal with exception here of not selecting a single experiment
			error_popup=Popup(title='Error',content=Label(text="Email cannot be left blank")\
					,size_hint=(.75,.75),auto_dismiss=True)
			error_popup.open()
			Clock.schedule_interval(error_popup.dismiss, 3)
		else:
			self.store.put('credentials', username=self.t.text)
			self.username=self.store.get('credentials')['username']
			exp_data.set_username(self.username)
			self.parent.current = 'ExperimentSelectScreen'
		
class ExperimentSelectScreen(Screen):
	def call_popup(self):
		box = BoxLayout(orientation= 'vertical')
		self.filename=TextInput(text='',font_size= sp(25))
		box.add_widget(self.filename)
		close_button=Button(text='Ok',size_hint=(.5,.5),pos_hint={'right': 0.75})
		box.add_widget(close_button)
		self.popup = Popup(title='Enter Experiment Name',content=box,size_hint=(1,.35),auto_dismiss=True)
		close_button.bind(on_release=self.exp_button_clicked)
		self.popup.open()
	def exp_button_clicked(self,btn):
			if(len(self.filename.text)!=0) and (any(char in set(string.punctuation.replace("_", "")) for char in self.filename.text)) == False: #deals with exception of empty filename
				root_dir= App.get_running_app().user_data_dir
				with open(root_dir+'/'+self.filename.text+'.csv','w') as csvfile:
					fieldnames = ['No. of steps', 'Centre','Time taken(secs)','No. of exiting ppl'\
					,'Date','Time','Place','Valid','Username']
					csvfile.write (','.join(fieldnames)+'\n')
				self.popup.dismiss()
				file_confirm= Popup(title='Confirmation',content=Label(text='File saved at \n'+root_dir+\
					'/'+self.filename.text+'.csv'),size_hint=(.75,.75))
				file_confirm.open()
				Clock.schedule_interval(file_confirm.dismiss, 3)
			else:
				error_popup=Popup(title='Error',content=Label(text="Experiment name cannot be empty nor contain \nspaces and special characters apart from underscores.")\
					,size_hint=(1,.4),auto_dismiss=True)
				error_popup.open()
				Clock.schedule_interval(error_popup.dismiss, 3)
	def select_experiment(self):
		file_system = FileSystemLocal()
		file_list=file_system.listdir(App.get_running_app().user_data_dir+'/')   # this returns a list of files in dir
		file_list=[x for x in file_list if x[-4:]=='.csv']
		if len(file_list)>0:
			box = BoxLayout(orientation= 'vertical')
			s=ScrollView(size_hint_y=0.80)
			g=GridLayout(cols=1,size_hint_y=None)
			for exp_file in file_list:
				g.add_widget(ToggleButton(text=exp_file, group='experiment',size_hint_y= None,height=90))
			g.bind(minimum_height=g.setter('height'))
			s.add_widget(g)
			box.add_widget(s)
			close_button=Button(text='Ok',size_hint=(.25,.15),pos_hint={'right': (0.75+0.5)/2})
			box.add_widget(close_button)
			close_button.bind(on_release=self.file_button_clicked)
			self.select_exp=Popup(title='Select Experiment',content=box,size_hint=(.75,.75),auto_dismiss=True)
			self.select_exp.open()
		else:
			error_popup=Popup(title='Error',content=Label(text="Please create a experiment before.")\
					,size_hint=(.80,.40),auto_dismiss=True)
			error_popup.open()
			Clock.schedule_interval(error_popup.dismiss, 3)

	def file_button_clicked(self,btn):
		exp_data.clear_object()
		button_selected=[t for t in ToggleButton.get_widgets('experiment') if t.state=='down']
		if len(button_selected) != 0:         #deal with exception here of not selecting a single experiment
			current = button_selected[0]
			exp_data.update_filename(current.text,App.get_running_app().user_data_dir+'/'+current.text)
			self.select_exp.dismiss()
			self.parent.current = 'StartExperiment'
		else:
			error_popup=Popup(title='Error',content=Label(text="Please select a experiment before\nproceeding.")\
					,size_hint=(.80,.40),auto_dismiss=True)
			error_popup.open()
			Clock.schedule_interval(error_popup.dismiss, 3)
				  
class StartExperiment(Screen):
	sw_started = False
	sw_seconds = 0
	started = False
	def __init__(self,**kwargs):
		self.started=False
		super(StartExperiment, self).__init__(**kwargs)

	def start_stop(self):
		self.ids.start_stop.text = ('Start' if self.sw_started else 'Stop')
		self.sw_started = not self.sw_started

	def on_start(self):
		if self.started == False:
			print"_"*100
			Clock.schedule_interval(self.update, 0)
			self.started= True
	def reset(self):
		if self.sw_started:
			self.ids.start_stop.text = 'Start'
			self.sw_started = False
		self.sw_seconds = 0

	def update(self, nap):
		if self.sw_started:
			self.sw_seconds += nap
		m, s = divmod(self.sw_seconds, 60)
		self.ids.stopwatch.text = ('%02d:%02d.[size=40]%02d[/size]' %
										(int(m),int(s), int(s * 1000 % 1000)))
	def save_data(self): 
		num_of_exit_ppl=0;num_of_steps=0;centre=''     
		if len(self.ids.num_of_steps.text)!=0:
			try:
				num_of_steps=float(self.ids.num_of_steps.text)            
			except ValueError:
				num_of_steps=""
				error_popup=Popup(title='Error',content=Label(text="Only numeric values allowed for number of exit people. Your input is dismissed.\nReturn to previous menu and return again.")\
					,size_hint=(.75,.75),auto_dismiss=True)
				error_popup.open()
				Clock.schedule_interval(error_popup.dismiss, 3) 
		if len(self.ids.num_of_exit_ppl.text)!=0:
			try:
				num_of_exit_ppl= float(self.ids.num_of_exit_ppl.text)
			except ValueError:
				num_of_exit_ppl=""
				error_popup=Popup(title='Error',content=Label(text="Only numeric values allowed for number of steps. Your input is dismissed.\nReturn to previous menu and return again.")\
					,size_hint=(.75,.75),auto_dismiss=True)
				error_popup.open()
				Clock.schedule_interval(error_popup.dismiss, 3)
		mins=float(self.ids.stopwatch.text[:2])
		secs= float(self.ids.stopwatch.text[3:5])
		milli_secs=float(re.findall(r'](\w+)\[', self.ids.stopwatch.text)[0])
		time_to_exit=(mins*60+secs+0.001*milli_secs) #check this conversion
		if len(self.ids.centre.text[0]) !=0:
			centre=self.ids.centre.text[0].lower()
		exp_date_time=datetime.now().strftime('%d-%m-%y %H:%M:%S')
		exp_data.update_exp_data(num_of_exit_ppl,num_of_steps,time_to_exit,exp_date_time[:8]
			,exp_date_time[9:],centre)

		#exp_data.print_data()

class Location(Screen):
	def save_data(self):
		valid='';location=''
		if len(self.ids.valid.text) !=0:
			valid=self.ids.valid.text[0].lower()
		if len(self.ids.location.text) !=0:
			location=self.ids.location.text
		exp_data.update_location_valid(valid,location)
		exp_data.write_data()
	def get_stations(self):
		list_stations=([line.rstrip('\n').replace('\t','').replace('\r','') for line in open('metro_stations.txt')])
		return tuple(sorted(list_stations, key=lambda s: s.lower()))

class Instructions(Screen):
	 def get_instructions(self):
	 	t=''
		with open ("instructions.txt", "r") as myfile:
			t= myfile.read().replace('\r','\n')
		return t.replace('\t',' '*4)
class DeleteScreen(Screen):
	result_label=''
	check_boxes={}
	b=''
	def __init__(self,**kwargs):
		self.name='DeleteScreen'
		super(DeleteScreen, self).__init__(**kwargs)
	def update_file_layout(self):
		self.clear_widgets()  
		self.check_boxes={}
		b=BoxLayout(orientation='vertical')
		file_system = FileSystemLocal()
		file_list=file_system.listdir(App.get_running_app().user_data_dir+'/')   # this returns a list of files in dir
		file_list=[x for x in file_list if x[-4:]=='.csv']
		b.add_widget(Label(text='Select files to be deleted',bold=True,font_size=sp(25),size_hint_y= 0.1))
		s=ScrollView(size_hint_y=0.75)
		g=GridLayout(cols=2,size_hint_y=None)
		for file_1 in file_list:
			c=CheckBox()
			l=Label(bold= True,font_size=sp(20),text=file_1,size_hint_y= None,height=70)
			self.check_boxes[c]=file_1
			g.add_widget(l);g.add_widget(c)
		g.bind(minimum_height=g.setter('height'))
		s.add_widget(g)
		b.add_widget(s)
		g_options=GridLayout(cols=2,size_hint_y= 0.10)
		g_options.add_widget(Button(text="Delete",on_press=self.create_result,font_size=sp(25)))
		g_options.add_widget(Button(text="Back",on_press=self.return_back,font_size=sp(25)))
		b.add_widget(g_options)
		self.add_widget(b)        
	def return_back(self,btn):
		self.parent.current = 'ExperimentSelectScreen'

	def create_result(self,btn):
		file_list=[]
		root_dir= App.get_running_app().user_data_dir+'/'
		for key, value in self.check_boxes.iteritems():
			if key.active==True:
				file_list.append(root_dir+'/'+value)
		print file_list
		if len(file_list) !=0:
			for file_delete in file_list:
				os.remove(file_delete)
		else:
			error=Popup(title='Error',content=Label(text="Please select files to be deleted")\
					,size_hint=(.50,.50),auto_dismiss=True)
			error.open()
			Clock.schedule_interval(error.dismiss, 3)
		self.update_file_layout()

class SendData(Screen):
	check_boxes={}
	file_list=[]
	popup_uploading=[]
	popup_uploaded=[]
	file_names=[]
	def __init__(self,**kwargs):
		self.name='SendData'
		super(SendData, self).__init__(**kwargs)
	def update_file_layout(self):
		auth_token='S2_xUq0_iNAAAAAAAAAACYNG1zf1GAzKpVWVfmLcZLA-FIiSlGxMvmxBkAtspuWQ'
		client = dropbox.client.DropboxClient(auth_token)
		self.clear_widgets()  
		b=BoxLayout(orientation='vertical')
		file_system = FileSystemLocal()
		root_dir= App.get_running_app().user_data_dir+'/';result_dir=root_dir+'results'
		file_list=file_system.listdir(root_dir)   # this returns a list of files in dir
		if os.path.exists(result_dir):file_list.extend(file_system.listdir(App.get_running_app().user_data_dir+'/'+'results'+'/'))
		file_list=[x for x in file_list if x[-4:]=='.csv']
		b.add_widget(Label(text='Select Files to Upload',bold=True,font_size=sp(25),size_hint_y= 0.1))      
		file_system = FileSystemLocal()
		file_list=file_system.listdir(App.get_running_app().user_data_dir+'/')   # this returns a list of files in dir
		file_list=[x for x in file_list if x[-4:]=='.csv']
		s=ScrollView(size_hint_y=0.75)
		g=GridLayout(cols=2,size_hint_y=None)
		for file_1 in file_list:
			c=CheckBox(active=False)
			l=Label(bold= True,font_size=sp(20),text=file_1,size_hint_y= None,height=70)
			self.check_boxes[c]=file_1
			g.add_widget(l);g.add_widget(c)
		g.bind(minimum_height=g.setter('height'))
		s.add_widget(g)
		b.add_widget(s)
		g_options=GridLayout(cols=2,size_hint_y= 0.1,orientation='horizontal')       
		g_options.add_widget(Button(text="Send",on_press=self.upload,font_size=sp(25)))
		g_options.add_widget(Button(text="Back",on_press=self.return_back,font_size=sp(25)))
		b.add_widget(g_options)
		self.add_widget(b)

	def return_back(self,btn):
		self.parent.current = 'ExperimentSelectScreen'
	def upload_files(self):
		auth_token='S2_xUq0_iNAAAAAAAAAACYNG1zf1GAzKpVWVfmLcZLA-FIiSlGxMvmxBkAtspuWQ'
		for file_name,file_to_upload in zip(self.file_names,self.file_list):
			f = open(file_to_upload, 'rb')
			client = dropbox.client.DropboxClient(auth_token)        
			response = client.put_file(file_name[:-4]+'_'+exp_data.username.rsplit('@', 1)[0]+'.csv', f)
		self.uploaded()

	@mainthread
	def uploaded(self):
		self.popup_uploading.dismiss()
		self.popup_uploaded=Popup(title='',content=Label(text="Uploaded!"),size_hint=(1,.75),auto_dismiss=True)
		self.popup_uploaded.open()
		for check_box in self.check_boxes:
			check_box.active=False
		Clock.schedule_once(self.popup_uploaded.dismiss, 1)

	def upload(self,btn):
		self.file_list=[]
		self.file_names=[]
		root_dir= App.get_running_app().user_data_dir#+'/'
		print root_dir
		for key, value in self.check_boxes.iteritems():
			if key.active==True:
				print value
				self.file_list.append(root_dir+'/'+value)
				self.file_names.append(value)
		if len(self.file_names)!=0:
			self.popup_uploading=Popup(title='',content=Label(text="Uploading right now.."),size_hint=(1,.75),auto_dismiss=True)
			self.popup_uploading.open()
			t = threading.Thread(target= self.upload_files)
			t.start()
		else:
			error=Popup(title='Error',content=Label(text="Please select files to be uploaded")\
					,size_hint=(.50,.50),auto_dismiss=True)
			error.open()
			Clock.schedule_interval(error.dismiss, 3)
#ScreenManager
class AppScreenManager(ScreenManager):
	pass

#Base Class
class AppBaseClass(App):
	def build(self):
		return Builder.load_file('appbase.kv')

if __name__ == '__main__':
	exp_data=Experiment_Data()
	AppBaseClass().run()