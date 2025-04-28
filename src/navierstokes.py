import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class NavierStokesSimulator:
    """
    A class for simulating 2D incompressible fluid flow using the Navier-Stokes equations.
    Uses a simplified approach with the Chorin's projection method.
    """
    
    def __init__(self, width, height, viscosity=0.1, dt=0.1):
        """
        Initialize the simulator with a grid of specified dimensions.
        
        Args:
            width (int): Width of the simulation grid
            height (int): Height of the simulation grid
            viscosity (float): Fluid viscosity coefficient
            dt (float): Time step size
        """
        self.width = width
        self.height = height
        self.viscosity = viscosity
        self.dt = dt
        
        # Initialize velocity fields (u is horizontal, v is vertical)
        self.u = np.zeros((height, width))
        self.v = np.zeros((height, width))
        
        # Previous velocity fields
        self.u_prev = np.zeros((height, width))
        self.v_prev = np.zeros((height, width))
        
        # Density/pressure field
        self.density = np.zeros((height, width))
        
    def add_density(self, x, y, amount):
        """Add density at a specific position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.density[y, x] += amount
            
    def add_velocity(self, x, y, amount_x, amount_y):
        """Add velocity at a specific position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.u[y, x] += amount_x
            self.v[y, x] += amount_y
    
    def diffuse(self, field, field_prev, diffusion_rate):
        """
        Diffuse a field (velocity or density) according to the diffusion equation.
        Uses Gauss-Seidel relaxation to solve the linear system.
        """
        a = self.dt * diffusion_rate * self.width * self.height
        
        # Copy the field
        field[:] = field_prev[:]
        
        # Iterative solver (Gauss-Seidel relaxation)
        for k in range(20):  # Number of iterations
            for i in range(1, self.height-1):
                for j in range(1, self.width-1):
                    field[i, j] = (field_prev[i, j] + a * (
                        field[i+1, j] + field[i-1, j] + 
                        field[i, j+1] + field[i, j-1]
                    )) / (1 + 4 * a)
            
            # Apply boundary conditions
            self._set_boundary(field)
    
    def advect(self, field, field_prev, u, v):
        """
        Advect a field (velocity or density) according to the velocity field.
        Uses a semi-Lagrangian approach.
        """
        dt0 = self.dt * np.sqrt(self.width * self.height)
        
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                # Trace particle back in time
                x = j - dt0 * u[i, j]
                y = i - dt0 * v[i, j]
                
                # Clamp coordinates
                x = max(0.5, min(self.width-1.5, x))
                y = max(0.5, min(self.height-1.5, y))
                
                # Find grid cell containing the traced-back position
                i0, j0 = int(y), int(x)
                i1, j1 = i0+1, j0+1
                
                # Bilinear interpolation weights
                s1 = x - j0
                s0 = 1 - s1
                t1 = y - i0
                t0 = 1 - t1
                
                # Bilinear interpolation
                field[i, j] = (
                    t0 * (s0 * field_prev[i0, j0] + s1 * field_prev[i0, j1]) +
                    t1 * (s0 * field_prev[i1, j0] + s1 * field_prev[i1, j1])
                )
        
        # Apply boundary conditions
        self._set_boundary(field)
    
    def project(self):
        """
        Project the velocity field to make it divergence-free (incompressible flow).
        Uses the Helmholtz-Hodge decomposition.
        """
        # Calculate divergence
        div = np.zeros((self.height, self.width))
        p = np.zeros((self.height, self.width))
        
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                div[i, j] = -0.5 * (
                    self.u[i, j+1] - self.u[i, j-1] +
                    self.v[i+1, j] - self.v[i-1, j]
                ) / np.sqrt(self.width * self.height)
        
        # Apply boundary conditions
        self._set_boundary(div)
        self._set_boundary(p)
        
        # Solve Poisson equation using Gauss-Seidel relaxation
        for k in range(20):
            for i in range(1, self.height-1):
                for j in range(1, self.width-1):
                    p[i, j] = (div[i, j] + p[i+1, j] + p[i-1, j] + p[i, j+1] + p[i, j-1]) / 4
            
            self._set_boundary(p)
        
        # Subtract gradient of pressure from velocity
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                self.u[i, j] -= 0.5 * (p[i, j+1] - p[i, j-1]) * self.width
                self.v[i, j] -= 0.5 * (p[i+1, j] - p[i-1, j]) * self.height
        
        # Apply boundary conditions
        self._set_boundary(self.u)
        self._set_boundary(self.v)
    
    def _set_boundary(self, field):
        """Apply boundary conditions (no-slip at the walls)"""
        # Set edges
        field[0, :] = 0
        field[-1, :] = 0
        field[:, 0] = 0
        field[:, -1] = 0
        
        # Set corners
        field[0, 0] = 0.5 * (field[1, 0] + field[0, 1])
        field[0, -1] = 0.5 * (field[1, -1] + field[0, -2])
        field[-1, 0] = 0.5 * (field[-2, 0] + field[-1, 1])
        field[-1, -1] = 0.5 * (field[-2, -1] + field[-1, -2])
    
    def step(self):
        """Perform one simulation step"""
        # Save previous velocity fields
        self.u_prev[:] = self.u[:]
        self.v_prev[:] = self.v[:]
        
        # Diffusion step for velocity
        self.diffuse(self.u, self.u_prev, self.viscosity)
        self.diffuse(self.v, self.v_prev, self.viscosity)
        
        # Projection to enforce incompressibility
        self.project()
        
        # Save velocity fields again after projection
        self.u_prev[:] = self.u[:]
        self.v_prev[:] = self.v[:]
        
        # Advection step for velocity
        self.advect(self.u, self.u_prev, self.u_prev, self.v_prev)
        self.advect(self.v, self.v_prev, self.u_prev, self.v_prev)
        
        # Projection again
        self.project()
        
        # Diffusion step for density
        density_prev = self.density.copy()
        self.diffuse(self.density, density_prev, 0.01)  # Diffusion rate for density
        
        # Advection step for density
        density_prev = self.density.copy()
        self.advect(self.density, density_prev, self.u, self.v)


def simulate_fluid_flow():
    """Run a fluid simulation with visualization"""
    # Create simulator
    width, height = 100, 100
    sim = NavierStokesSimulator(width, height, viscosity=0.0001, dt=0.1)
    
    # Setup figure for visualization
    fig, ax = plt.subplots(figsize=(8, 8))
    img = ax.imshow(sim.density, cmap='hot', vmin=0, vmax=1)
    
    # Add initial conditions - a circular density in the center
    center_x, center_y = width // 2, height // 2
    radius = 10
    
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
            if dist < radius:
                sim.add_density(j, i, 1.0)
    
    # Add some initial velocity
    for i in range(center_y-radius, center_y+radius):
        for j in range(center_x-radius, center_x+radius):
            sim.add_velocity(j, i, 0, -50)  # Upward velocity
    
    # Animation update function
    def update(frame):
        # Add some density and velocity periodically
        if frame % 20 == 0:
            for i in range(5):
                sim.add_density(center_x, center_y + radius, 0.5)
                sim.add_velocity(center_x, center_y + radius, 0, -50)
        
        # Step the simulation
        sim.step()
        
        # Update the visualization
        img.set_array(sim.density)
        return [img]
    
    # Create animation
    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=True)
    plt.title('Navier-Stokes Fluid Simulation')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    simulate_fluid_flow()
