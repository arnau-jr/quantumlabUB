#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manu Canals Codina

Eigenvalues and eigenfunctions of a time-independent potential (Hamiltonian).
"""
#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

#Potential.
def gaussian(mu, sigma, x):
    f = 1./np.sqrt(2*np.pi*sigma**2)*np.exp(-(x-mu)**2/(2.*sigma**2))
    return f

def harmonic(k, x):
    V = 0.5*k*x**2
    return V

def poten(x):
    pot = 10*2*(0.4*gaussian(0, 0.6, x) + harmonic(0.1, x))  #Potential
    #Factor 10 introduced to minimize the influence of the walls, since a 
    #larger potential keeps the main structure of the wave function centered.
    return pot

def eigenparam(a, b, N, m, poten):
    """
    Returns the a vector with the eigenvalues and another with the eigenvectors
    (each eigenvector of dimention N). It solves the time-independent 
    Schrödinger equation for a given potentitial [poten] inside of a 
    box [a, b], with [N] intervals. [m] := hbar**2 / M  (M = mass) 
    """
    deltax = (b-a)/float(N)
    
    #Dividing the ab segment in N intervals leave us with a (N+1)x(N+1) 
    #hamiltonian, where indices 0 and N correspond to the potentials barriers.
    #The hamiltonian operator has 3 non-zero diagonals (the main diagonal, and
    #the ones next to it), with the following elements.
    
    H = np.zeros((N+1,N+1))
    
    H[0,0] = 1./(m*deltax**2) + 1000000000
    H[N,N] = 1./(m*deltax**2) + 1000000000
    H[1,0] = -1./(2.*m*deltax**2)
    H[N-1,N] = -1./(2.*m*deltax**2)
    
    for i in range(1, N):
        H[i,i] = 1./(m*deltax**2) + poten(a + deltax*i)
        H[i-1,i] = -1./(2.*m*deltax**2)
        H[i+1,i] = -1./(2.*m*deltax**2)
        
    #Diagonalizing H we'll get the eigenvalues and eigenvectors (evect 
    #in columns).
    evals, evect = np.linalg.eigh(H)
    
    #Normalization
    factor = np.zeros((N+1)) #Evect will be multiplied by 1/sqrt(factor)
    #Integrating with trapezoids
    for col in range(N+1):
        for line in range(N):
            #The area of one trapezoid is added every iteration
            factor[col] += ( (np.abs(evect[line,col]))**2 + 
                          (np.abs(evect[line+1,col]))**2 )*deltax / 2.
                  
    #Check if the sum of all components of any evect gives 1
    check = 0
    for elem in evect[:,40]:
        check += elem**2    
    #print(check)
    
    #Normalized vectors
    for col in range(N+1):
        evect[:,col] *= 1/np.sqrt(factor[col])
         
    return evals, evect

def norm(vector, dx):
    """
    Computes the norm of the vector integrating with trapezoids of witdh dx.
    """
    #With dx constant, the following formula can be deduced.
    n = dx * (sum(vector) - vector[0]/2. - vector[-1]/2.)
    return n

#%%
#Check normalization and first run of eigenparam (results used later)
a = -5.
b= 5.
N = 100
m = 1
dx = (b-a)/float(N)

pvals, pvect = eigenparam(a, b, N, m, poten)

normm = np.zeros((N+1))

for col in range(N+1):
    for line in range(N):
        #Area of one trapezoid is added every iteration
        normm[col] += ( (np.abs(pvect[line,col]))**2 + 
                      (np.abs(pvect[line+1,col]))**2 )*dx / 2.

#print(normm[7])            
#print(norm((np.abs(pvect[:,7]))**2, dx))
            
#x = np.linspace(a, b, N+1)
#plt.title('Factor del potencial')
#plt.plot(x, 0.1*poten(x))
#plt.plot(x, poten(x))
#%%

#plt.plot(pvect[:,3])
#plt.plot(pvect[:,450])
#plt.plot(pvect[:,100])
#plt.plot(pvect[:,250])

#plt.yscale('log')
#plt.plot(pvals)

#%%

#Projection of the given intial wave function onto the basis {evect}
#Initial wave function

def psi0(points):
    """
    Generates a vector with the values of the initial wave function in the 
    given points (psi0 dimension same as points).
    Wave function introduced here explicitly.
    
    """
    #In this case psi0 is a gaussian packet (as an example)
    mu = points[int(len(points)*0.4)] 
    sigma0 = 0.5
    p0 = 0.5 #momentum
    wavef = np.sqrt((1./(np.sqrt(2*np.pi)*sigma0))*np.exp(-(points-mu)**2/
                     (2.*sigma0**2)))*np.exp(complex(0,-1)*p0*points)
    return wavef

def comp(evect, psi, deltax):
    """
    Given a basis evect and a vector psi, returns psi's components.
    """
    compo = []
    for ev in np.transpose(evect):
        integrand =[np.conjugate(v)*p for v, p in zip(ev, psi)] 
        compo.append(deltax*(sum(integrand)-integrand[0]/2.-integrand[-1]/.2))
        
    return compo
    
mesh = np.arange(a, b + (b-a)/float(N), ((b-a)/float(N)))
psi = psi0(mesh)

#print(norm((np.abs(psi))**2, dx))

#plt.plot(psi)

psicomp = comp(pvect,psi,(b-a)/float(N))
#print(proj, pvals)
#plt.title('Components de psi0')
#plt.xlim(0,30)
#plt.plot(psicomp)

#%%
#Animation (using all the components)
# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(a, b), ylim=(0, 1))
line, = ax.plot([], [], lw=2)
pot, = ax.plot([], [], lw = 1)

# initialization function (of each frame): plot the background
def init():
    line.set_data([], [])
    x = np.linspace(a, b, N+1)
    y = poten(x)/10.#It's the factor explined in poten, we rescale the 
                    #potential here so it fits in the plot.
    pot.set_data(x, y)
    return line,

# animation function.  This is called sequentially
def fullanimate(t):  
    x = np.linspace(a, b, N+1)
    y = []
    for i in range(0, N+1): #each component
        acum = 0
        for j in range(0, N+1): #each eigenvector
            acum += psicomp[j]*pvect[i,j]*np.exp(complex(0,-1)*pvals[j]*t/5)
        y.append((np.abs(acum))**2)
    
    line.set_data(x, y)
    
    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, fullanimate, init_func=init, frames=100, 
                                                       interval=100, blit=True)

anim.save('psievo.gif')

plt.show()

#%%

#Truncated alternative
#Lets calculate how far can we cut off comparing tpsi (truncated) with psi0
diff = []
psinorm = norm((np.abs(psi))**2, dx)
for lv in range(0,N+1): #las vector added
    tpsi = []
    for i in range(0, N+1): #each component
        acum = 0
        for j in range(0, lv+1): #each eigenvector up to lv (included)
            acum += psicomp[j] * pvect[i,j]  #t = 0
        tpsi.append(acum)
    #Lets use the normalization condition to compare how much they differ
    diff.append(abs(psinorm - norm((np.abs(tpsi))**2, dx)))
    
plt.title('Diferència(abs) de la norma entre psi truncada i sencera')
plt.yscale('log')
plt.plot(diff)
#Here we see that we hit machine presicion with lv around 40.
#%%






#%%
#Animation with psi truncated
top_vect = 7

#Study
studyx = 50
study = []
# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(a, b), ylim=(0, 1))
t_line, = ax.plot([], [], lw=2)
f_line, = ax.plot([], [], lw=2)
pot, = ax.plot([], [], lw = 1)

# initialization function (of each frame): plot the background
def init():
    t_line.set_data([], [])
    f_line.set_data([], [])
    x = np.linspace(a, b, N+1)
    y = poten(x)/10.#It's the factor explined in poten, we rescale the 
                    #potential here so it fits in the plot.
    pot.set_data(x, y)
    return t_line, f_line,

# animation function.  This is called sequentially
def trunc_animate(t):  
    x = np.linspace(a, b, N+1)
    
    y = [] #Truncated values
    for i in range(0, N+1): #each component
        acum = complex(0,0)
        for j in range(0, top_vect+1): #each eigenvector up to top_vect (incld)
            acum += psicomp[j]*pvect[i,j]*np.exp(complex(0,-1)*pvals[j]*t/5)
        y.append((np.abs(acum))**2)
        if i == studyx:
            trunc = (np.abs(acum))**2
    t_line.set_data(x, y)
    
    z = [] #Full values
    for i in range(0, N+1): #each component
        acum = complex(0,0)
        for j in range(0, N+1): #each eigenvector
            acum += psicomp[j]*pvect[i,j]*np.exp(complex(0,-1)*pvals[j]*t/5)
        z.append((np.abs(acum))**2)
        if i == studyx:
            study.append([t,np.abs(trunc-(np.abs(acum))**2)])
    
    f_line.set_data(x, z)
    
    
    return t_line, f_line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, trunc_animate, init_func=init, frames=100, 
                                                       interval=100, blit=True)

anim.save('tpsievo.gif')

plt.show()

#%%
