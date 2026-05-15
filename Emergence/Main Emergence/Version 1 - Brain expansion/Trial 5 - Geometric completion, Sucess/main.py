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
    
    if spawn_timer > 10:
        spawn_timer = 0
        
        to_add = set()
        to_remove = []
        
        # Optimization: Map grid positions to agents for O(1) lookups
        grid_to_agent = {to_grid(a): a for a in emergence_agents}

        for gx, gy in occupied:
            
            # Check for neighbors in the 3x3 grid around (gx, gy)
            up_left = (gx - 1, gy - 1) in occupied
            up = (gx, gy - 1) in occupied
            up_right = (gx + 1, gy - 1) in occupied
            
            left = (gx - 1, gy) in occupied
            right = (gx + 1, gy) in occupied
            
            down_left = (gx - 1, gy + 1) in occupied
            down = (gx, gy + 1) in occupied
            down_right = (gx + 1, gy + 1) in occupied
            
            did_remove = False
            
            # Calculate total neighbor density (0 to 8)
            neighbor_count = sum([up_left, up, up_right, left, right, down_left, down, down_right])

            # --- RULE 4.3: OVERCROWDING DECAY ---
            if neighbor_count >= 5:
                to_remove.append(grid_to_agent.get((gx, gy)))
                did_remove = True

            # --- RULE 4.1: DECAYING (Lone Remnants) ---
            if not did_remove and len(emergence_agents) == 2 and neighbor_count == 0:
                if not to_remove:
                    to_remove.append(grid_to_agent.get((gx, gy)))
                    did_remove = True

            # --- RULE 5: GEOMETRIC COMPLETION (Order from Chaos) ---
            is_part_of_square = False
            if up and left and up_left: is_part_of_square = True
            if up and right and up_right: is_part_of_square = True
            if down and left and down_left: is_part_of_square = True
            if down and right and down_right: is_part_of_square = True

            # If we aren't in a square but have the L-shape, complete it
            if not is_part_of_square:
                if up and left: to_add.add((gx - 1, gy - 1))
                if up and right: to_add.add((gx + 1, gy - 1))
                if down and left: to_add.add((gx - 1, gy + 1))
                if down and right: to_add.add((gx + 1, gy + 1))

            # --- RULE 3: STABILITY CONTROL (Triple Connection) ---
            if not did_remove and ((left and right) or (up and down)):
                # Add another in random axis
                rx, ry = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                to_add.add((gx + rx, gy + ry))

                # Identify candidates for removal
                candidates = []
                if left and right:
                    candidates += [grid_to_agent.get((gx - 1, gy)), grid_to_agent.get((gx + 1, gy))]
                if up and down:
                    candidates += [grid_to_agent.get((gx, gy - 1)), grid_to_agent.get((gx, gy + 1))]
                
                # Filter candidates: Avoid removing pixels that are already part of a stable square
                loose_candidates = []
                for c in candidates:
                    if c is not None:
                        # A simple check: if the candidate has few neighbors, it's "loose"
                        c_grid = to_grid(c)
                        # We prioritize removing pixels that aren't helping form a 2x2
                        loose_candidates.append(c)
                
                candidates = loose_candidates if loose_candidates else [c for c in candidates if c]
                
                if candidates:
                    to_remove.append(random.choice(candidates))
                    did_remove = True
                    
            if not did_remove:
                if not (left or right or up or down):
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    to_add.add((gx + dx, gy + dy))

                if left ^ right:
                    dy = random.choice([-1, 1])
                    to_add.add((gx, gy + dy))

                if up ^ down:
                    dx = random.choice([-1, 1])
                    to_add.add((gx + dx, gy))
        
        if to_remove:
            remove_ids = {id(a) for a in to_remove}
            emergence_agents = [a for a in emergence_agents if id(a) not in remove_ids]
        
        occupied = set(to_grid(a) for a in emergence_agents)
        
        for cell in to_add:
            if cell not in occupied:
                emergence_agents.append(
                    pygame.Vector2(cell[0]*cell_size, cell[1]*cell_size)
                )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
