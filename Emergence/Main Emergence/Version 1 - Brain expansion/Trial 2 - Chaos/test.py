import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

pygame.display.set_caption("Emergence Simulation")         

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
    
    # Circle
    # pygame.draw.circle(screen, (255, 255, 255), emergence_agent, 5)   
    
    # A single Pixel
    # screen.set_at((int(emergence_agent.x), int(emergence_agent.y)), (255, 255, 255))
    
    # MAIN CODE
    
    # A square
    # pygame.draw.rect(screen, (255, 255, 255), (emergence_agent.x, emergence_agent.y, 5, 5))
    occupied = set()
    
    for agent in emergence_agents:
        pygame.draw.rect(screen, (255, 255, 255), (agent.x, agent.y, 5, 5))
        occupied.add(to_grid(agent))

    # for agent in emergence_agents:
    #     occupied.add(to_grid(agent))

    spawn_timer += 1

    if spawn_timer > 30:
        spawn_timer = 0

        to_add = set()
        to_remove = []
        
        # Optimization: Map grid positions to agents for O(1) lookups.
        # This significantly improves performance as the number of agents grows.
        grid_to_agent = {to_grid(a): a for a in emergence_agents}

        for gx, gy in occupied:

            # Check for neighbors in the four cardinal directions.
            # This determines the local configuration around the current agent.
            left  = (gx - 1, gy) in occupied
            right = (gx + 1, gy) in occupied
            up    = (gx, gy - 1) in occupied
            down  = (gx, gy + 1) in occupied

            did_remove = False

            # --- RULE 3: STABILITY CONTROL (Triple Connection) ---
            # This rule triggers when a pixel is the middle of a 3-pixel line (horizontally or vertically).
            # If we just let pixels grow, they would form solid blocks or infinite lines.
            # Rule 3 introduces "entropy" by adding a new pixel nearby and then
            # deleting one of the existing neighbors. This makes the structures 
            # look like they are crawling or shifting rather than just growing.
            if (left and right) or (up and down):
                # Rule 3 says: add another one in a random axis...
                rx, ry = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                to_add.add((gx + rx, gy + ry))

                # ...then remove one of the existing pixels randomly
                if left and right:
                    # Direct lookup instead of scanning the whole list
                    candidates = [grid_to_agent.get((gx - 1, gy)), grid_to_agent.get((gx + 1, gy))]
                    candidates = [c for c in candidates if c is not None]
                    if candidates:
                        to_remove.append(random.choice(candidates))
                        did_remove = True

                if up and down and not did_remove: # Only remove from vertical if not already removed from horizontal
                    candidates = [grid_to_agent.get((gx, gy - 1)), grid_to_agent.get((gx, gy + 1))]
                    candidates = [c for c in candidates if c is not None]
                    if candidates:
                        to_remove.append(random.choice(candidates))
                        did_remove = True

                if up and down and not did_remove:
                    candidates = [grid_to_agent.get((gx, gy - 1)), grid_to_agent.get((gx, gy + 1))]
                    candidates = [c for c in candidates if c is not None]
                    if candidates:
                        to_remove.append(random.choice(candidates))
                        did_remove = True

            # --- RULE 1 & 2 (only if no removal) ---
            if not did_remove:

                # --- RULE 1: SEEDING (Isolated Pixel) ---
                # If a pixel has absolutely no neighbors in the 4 cardinal directions,
                # it is a "seed." It will immediately try to grow a neighbor in 
                # a random direction to start a colony.
                if not (left or right or up or down):
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    to_add.add((gx + dx, gy + dy))

               # --- RULE 2: BRANCHING (Pairs) ---
                # We use XOR (^) here. This triggers if there is a neighbor on 
                # ONE side but not the other (the ends of a 2-pixel segment).
                
                # If it's a horizontal pair end, grow vertically.
                if left ^ right:
                    dy = random.choice([-1, 1])
                    to_add.add((gx, gy + dy))

                # Rule 2: vertical pair → grow horizontal
                if up ^ down:
                    dx = random.choice([-1, 1])
                    to_add.add((gx + dx, gy))              
        
        # Efficient removal of agents. Using `id(a)` is faster than `a in emergence_agents`
        # for large lists, as it avoids iterating through the list to find the object.
        if to_remove:
            remove_ids = {id(a) for a in to_remove}
            emergence_agents = [a for a in emergence_agents if id(a) not in remove_ids]
        
        occupied = set(to_grid(a) for a in emergence_agents)
        
        # then add new aggents to simulation
        for cell in to_add:
            if cell not in occupied:
                emergence_agents.append(
                    pygame.Vector2(cell[0]*cell_size, cell[1]*cell_size)
                )
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()