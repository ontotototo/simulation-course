import tkinter as tk
from tkinter import Canvas
import numpy as np

EMPTY, TREE, FIRE, LAKE = 0, 1, 2, 3  

class ForestFireCA:
    def __init__(self, width=120, height=80, cell_size=6):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = np.zeros((height, width), dtype=int)
        self.next_grid = np.zeros((height, width), dtype=int)
        self.p = 0.04
        self.f = 0.01
        self.lakes = [(20,20,10,5), (60,40,8,4)]  
        
        # вероятности распространения по 8 направлениям (правый ветер)
        self.fire_prob = np.array([0.2, 0.3, 0.25, 0.5, 0.2, 0.25, 0.3, 0.2])
        
        self.grid[1:-1, 1:-1] = (np.random.random((height-2, width-2)) < 0.6).astype(int)
        self.init_lakes()  
        self.is_running = False
        self.speed = 300
        
    def init_lakes(self):
        for lx, ly, lw, lh in self.lakes:
            self.grid[ly:ly+lh, lx:lx+lw] = LAKE  
    
    def is_lake_pos(self, x, y):
        return any(ly <= y < ly+lh and lx <= x < lx+lw for lx, ly, lw, lh in self.lakes)
    
    def wind_neighbors(self, x, y):
        """Подсчет горящих соседей с учетом ветра"""
        dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        total_prob = 0
        max_prob = 0
        
        for i, (dx, dy) in enumerate(dirs):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[ny, nx] == FIRE:
                    prob = self.fire_prob[i]
                    total_prob += prob
                    if prob > max_prob:
                        max_prob = prob
        return total_prob > 0, max_prob
    
    def neighbors(self, x, y):
        dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        count = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[ny, nx] == FIRE:  
                    count += 1
        return count
    
    def update(self):
        self.next_grid.fill(0)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y, x]
                
                # Правило 1 озеро не горит
                if cell == LAKE:
                    self.next_grid[y, x] = LAKE
                    continue
                
                # правило  Огонь в пустая земля
                if cell == FIRE:
                    continue
                
                # правило3 Пустая в дерево с p=0.04
                if cell == EMPTY and np.random.random() < self.p:
                    self.next_grid[y, x] = TREE
                    continue
                
                # Правило Дерево с ВЕТРОМ
                if cell == TREE:
                    has_fire, wind_prob = self.wind_neighbors(x, y)
                    if has_fire and np.random.random() < wind_prob:
                        self.next_grid[y, x] = FIRE  
                        continue
                    if np.random.random() < self.f:
                        self.next_grid[y, x] = FIRE  # молния
                    else:
                        self.next_grid[y, x] = TREE
        self.grid, self.next_grid = self.next_grid, self.grid
    
    def click_fire(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y, x] == TREE or self.grid[y, x] == EMPTY:
                self.grid[y, x] = FIRE
                print(f" Костер от пьяных подростоков [{x}, {y}]!")
                self.draw()
    
    def toggle_pause(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.step()
    
    def step(self):
        if self.is_running:
            self.update()
            self.draw()
            self.root.after(self.speed, self.step)
    
    def draw(self):
        self.canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y, x]
                if cell == LAKE:
                    color = "blue" 
                elif cell == EMPTY:
                    color = "grey"
                elif cell == TREE:
                    color = "darkgreen"
                else:  
                    color = "orange"
                self.canvas.create_rectangle(x*self.cell_size, y*self.cell_size,
                                           (x+1)*self.cell_size, (y+1)*self.cell_size,
                                           fill=color, outline="")
    
    def reset(self):
        self.grid.fill(0)
        self.grid[1:-1, 1:-1] = (np.random.random((self.height-2, self.width-2)) < 0.6).astype(int)
        self.init_lakes()
        self.draw()
    
    def run(self):
        self.root = tk.Tk()
        self.root.title(" Лесной пожар с ветром ")
        self.canvas = Canvas(self.root, width=self.width*self.cell_size, 
                           height=self.height*self.cell_size, bg="black")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click_fire)
        self.canvas.focus_set()
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()
        tk.Button(btn_frame, text=" Старт/ Пауза", command=self.toggle_pause).pack(side=tk.LEFT)
        tk.Button(btn_frame, text=" Новый лес", command=self.reset).pack(side=tk.LEFT)
        
        self.draw()
        self.root.mainloop()

if __name__ == "__main__":
    sim = ForestFireCA()
    sim.run()
