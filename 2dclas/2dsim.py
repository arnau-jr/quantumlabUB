
import numpy as np
import matplotlib.pyplot as plt
from particle import *
from potentials import *

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty,ListProperty,NumericProperty,StringProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle,Color,Ellipse
from kivy.clock import Clock
from matplotlib import cm
import pickle

L = 200


T = 30
dt = 0.1


class main(BoxLayout):
    
    
    param0 = NumericProperty()
    param1 = NumericProperty()
    param2 = NumericProperty()
    param3 = NumericProperty()
    
    mass = NumericProperty()
    charge = 1.
    x0 = NumericProperty()
    y0 = NumericProperty()
    vx0 = NumericProperty()
    vy0 = NumericProperty()
    
    
    potentials = ListProperty()
    potentialsave = []
    particlestrings = ListProperty()
    particlesave = []
    particles = []
    init_conds = []
    
    plot_texture = ObjectProperty()
    
    
    def __init__(self, **kwargs):
        super(main, self).__init__(**kwargs)
        self.pot = Phi()
        self.set_texture()
        self.time = 0.
        self.T = 30
        self.speedindex = 3
        self.change_speed()
        
    def set_texture(self):
        L = 200
        dx = 1
        self.nx = int(L/dx)
        self.im = np.zeros((self.nx,self.nx),dtype=np.uint8)
        self.plot_texture = Texture.create(size=self.im.shape,colorfmt='luminance',bufferfmt='uint')
        
    def background(self):
        xx,yy, = np.meshgrid(np.linspace(-L/2.,L/2.,self.nx,endpoint=True),np.linspace(-L/2.,L/2.,self.nx,endpoint=True))
        self.im = np.zeros((self.nx,self.nx))
        if(self.pot.functions.size == 0):
            self.im = np.uint8(self.im)
        else:
            self.im = self.pot.val(xx,yy)
            self.im = self.im + np.abs(self.im.min())
            self.im = np.uint8(255.*(self.im/self.im.max()))
            
    def update_texture(self):
        L = 200
        dx = 1
        self.nx = int(L/dx)
        with self.plotbox.canvas:
            cx = self.plotbox.pos[0]
            cy = self.plotbox.pos[1]
            w = self.plotbox.size[0]
            h = self.plotbox.size[1]
            b = min(w,h)
            
            
            self.plot_texture.blit_buffer(self.im.reshape(self.im.size),colorfmt='luminance')
            Color(1.0,1.0,1.0)
            Rectangle(texture = self.plot_texture, pos = (cx,cy),size = (b,b))
            
        
    def update_parameters(self,touch):
        w = self.plotbox.size[0]
        h = self.plotbox.size[1]
        b = min(w,h)
        scale = b/200.
        x = (touch.pos[0] - b/2.)/scale
        y = (touch.pos[1] - b/2.)/scale

        if(self.menu.current_tab.text == 'Potentials'):
            self.param0slider.value = x
            self.param1slider.value = y
        if(self.menu.current_tab.text == 'Particles'):
            self.x0slider.value = x
            self.y0slider.value = y
            
    def add_pot_list(self):
        self.potentials.append('Gauss:x0 = {}, y0 = {}, V0 = {}, Sig = {}'.format(round(self.param0,2),round(self.param1,2),round(self.param2,2),round(self.param3,2)))
        self.potentialsave.append('Gauss:x0 = {}, y0 = {}, V0 = {}, Sig = {}'.format(round(self.param0,2),round(self.param1,2),round(self.param2,2),round(self.param3,2)))
        self.pot.add_function(gauss,dgaussx,dgaussy,[self.param0,self.param1,self.param2,self.param3])
        self.background()
        self.update_texture()
        
        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def reset_pot_list(self):
        self.pot.clear()
        self.potentials = []
        self.potentialsave =[]
        self.plotbox.canvas.clear()
        self.background()
        
        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
        
    def add_particle_list(self):
        self.particlestrings.append('P{}: m = {}, x0 = {}, y0 = {}, vx0 = {}, vy0 = {}'.format(len(self.particlestrings)+1,round(self.mass,2),round(self.x0,2),round(self.y0,2),round(self.vx0,2),round(self.vy0,2)))
        self.particlesave.append('P{}: m = {}, x0 = {}, y0 = {}, vx0 = {}, vy0 = {}'.format(len(self.particlestrings)+1,round(self.mass,2),round(self.x0,2),round(self.y0,2),round(self.vx0,2),round(self.vy0,2)))
        self.particles.append(Particle(self.mass,self.charge,np.ones([1,4]),dt))
        self.init_conds.append([self.x0,self.y0,self.vx0,self.vy0])
        
        with self.statuslabel.canvas:
            Color = (1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def reset_particle_list(self):
        self.particlestrings = []
        self.particlesave = []
        self.particles = []
        self.init_conds = []
        
        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
    
    def compute(self):
        with self.statuslabel.canvas:
            Color(1,0.1,0.1)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
        for i,p in enumerate(self.particles,0):
            p.ComputeTrajectoryF(self.init_conds[i],self.pot)
        print('Done')
        for p in self.particles:
            print(p.trajectory[-1,:])
            
        with self.statuslabel.canvas:
            Color(0,1,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def play(self):
        self.timer = Clock.schedule_interval(self.animate,0.04)
        self.running = True
    
    def pause(self):
        if(self.running==True):
            self.timer.cancel()
        else:
            pass
        
    def change_speed(self):
        sl = [1,2,5,10]
        if(self.speedindex == len(sl)-1):
            self.speedindex = 0
        else:
            self.speedindex += 1
        self.speed = sl[self.speedindex]
        self.speedbutton.text = str(self.speed)+'x'
    
    def stop(self):
        self.pause()
        self.time = 0
        self.plotbox.canvas.clear()
        self.update_texture()
    
    def save(self):
        savedata = np.array([self.pot.functions,self.pot.dfunctionsx,self.pot.dfunctionsy,self.potentialsave,self.particles,self.init_conds,self.particlesave])
        with open('save.dat','wb') as file:
            pickle.dump(savedata,file)
        
    def load(self):
        with open('save.dat','rb') as file:
            savedata = pickle.load(file)
        
        self.pot.functions = savedata[0]
        self.pot.dfunctionsx = savedata[1]
        self.pot.dfunctionsy = savedata[2]
        self.potentials = savedata[3]
        self.particles = savedata[4]
        self.init_conds = savedata[5]
        self.particlestrings = savedata[6]
        
        self.background()
        self.update_texture()
    def animate(self,interval):
        w = self.plotbox.size[0]
        h = self.plotbox.size[1]
        b = min(w,h)
        scalew = b/200.
        scaleh = b/200.
        self.plotbox.canvas.clear()
        self.update_texture()
        with self.plotbox.canvas:
            for p in self.particles:
                Color(1.0,0.0,0.0)
            
                Ellipse(pos=(p.trax(self.time)*scalew+w/2.-5.,p.tray(self.time)*scaleh+h/2.-5.),size=(10,10))
        
        self.time += interval*self.speed
        if(self.time >= self.T):
            self.time = 0.
            
            
class simApp(App):

    def build(self):
        return main()


if __name__ == '__main__':
    simApp().run()