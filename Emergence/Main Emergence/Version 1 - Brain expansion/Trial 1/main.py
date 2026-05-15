import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

pygame.display.set_caption("Emergence Simulation Order")

emergence_agent = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
emergence_agents = [emergence_agent]
spawn_timer = 0
cell_size = 5
neighbors = [
    (-1,-1), (0,-1), (1,-1),
    (-1, 0),         (1, 0),
    (-1, 1), (0, 1), (1, 1)
]

grid_x = int(emergence_agent.x // cell_size)
grid_y = int(emergence_agent.y // cell_size)

def to_grid(pos):
    return (int(pos.x // cell_size), int(pos.y // cell_size))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill((0, 0, 0))
    
    occupied = set()
    
    for agent in emergence_agents:
        pygame.draw.rect(screen, (255, 255, 255), (agent.x, agent.y, 5, 5))
        occupied.add(to_grid(agent))
    
    spawn_timer += 1
    
    if spawn_timer > 30:
        spawn_timer = 0
        
        to_add = set()
        to_remove = []
        
        grid_to_agent = {to_grid(a): a for a in emergence_agents}

        for gx, gy in occupied:
            up_left = (gx - 1, gy - 1) in occupied
            up = (gx, gy - 1) in occupied
            up_right = (gx + 1, gy - 1) in occupied
            left = (gx - 1, gy) in occupied
            right = (gx + 1, gy) in occupied
            down_left = (gx - 1, gy + 1) in occupied
            down = (gx, gy + 1) in occupied
            down_right = (gx + 1, gy + 1) in occupied
            
            did_remove = False
            
            if len(emergence_agents) == 2 and not (
                up_left or up or up_right or left or right or down_left or down or down_right
            ):
                if not to_remove:
                    to_remove.append(grid_to_agent.get((gx, gy)))
                    did_remove = True

            if (left and right) or (up and down):
                rx, ry = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                to_add.add((gx + rx, gy + ry))

                candidates = []
                if left and right:
                    candidates += [grid_to_agent.get((gx - 1, gy)), grid_to_agent.get((gx + 1, gy))]
                if up and down:
                    candidates += [grid_to_agent.get((gx, gy - 1)), grid_to_agent.get((gx, gy + 1))]
                
                candidates = [c for c in candidates if c is not None]
                if candidates:
                    to_remove.append(random.choice(candidates))
                    did_remove = True
                    
            if not did_remove:
                # --- RULE 1: SEEDING (Isolated Cardinal) ---
                # If an agent has no cardinal neighbors, it acts as a "seed".
                # It clones itself in a random cardinal direction to start a colony.
                # This ensures the simulation doesn't stop at single dots.
                if not (left or right or up or down):
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    to_add.add((gx + dx, gy + dy))

                # --- RULE 2: BRANCHING (Pair Endings) ---
                # Uses XOR (^) to find the "ends" of a 2-pixel segment (one neighbor exists).
                # To create non-linear shapes, growth happens perpendicularly.

                # Horizontal pair end -> Grow vertically
                if left ^ right:
                    dy = random.choice([-1, 1])
                    to_add.add((gx, gy + dy))

                # Vertical pair end -> Grow horizontally
                if up ^ down:
                    dx = random.choice([-1, 1])
                    to_add.add((gx + dx, gy))              
        
        # Efficient removal
        if to_remove:
            remove_ids = {id(a) for a in to_remove}
            emergence_agents = [a for a in emergence_agents if id(a) not in remove_ids]
        
        occupied = set(to_grid(a) for a in emergence_agents)
        
        # then add
        for cell in to_add:
            if cell not in occupied:
                emergence_agents.append(
                    pygame.Vector2(cell[0]*cell_size, cell[1]*cell_size)
                )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
