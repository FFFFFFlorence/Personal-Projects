import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

pygame.display.set_caption("v1 - Brain Expansion")

emergence_agents = [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)]
spawn_timer = 0
cell_size = 5       # controls pixel size

def to_grid(pos):
    return (int(pos.x // cell_size), int(pos.y // cell_size))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill((0, 0, 0))      # background color
    
    # main render loop
    occupied = set()
    for agent in emergence_agents:    
        pygame.draw.rect(screen, (255, 255, 255), (agent.x, agent.y, cell_size, cell_size))
        occupied.add(to_grid(agent))    
    
    spawn_timer += 1
    
    if spawn_timer > 10:
        spawn_timer = 0
        
        to_add = set()
        to_remove = []
        grid_to_agent = {to_grid(a): a for a in emergence_agents}
        
        for gx, gy in occupied:
            
            # Neighbor Check (3x3 grid)
            up_left     = (gx - 1, gy - 1) in occupied
            up          = (gx,     gy - 1) in occupied
            up_right    = (gx + 1, gy - 1) in occupied
            left        = (gx - 1, gy)     in occupied
            right       = (gx + 1, gy)     in occupied
            down_left   = (gx - 1, gy + 1) in occupied
            down        = (gx,     gy + 1) in occupied
            down_right  = (gx + 1, gy + 1) in occupied

            did_remove = False
            neighbor_count = sum([up_left, up, up_right, left, right, down_left, down, down_right])
            
            # -------------------- RULES --------------------
            # --- RULE 4.3 - saturation decay --- 
            if neighbor_count >= 5:
                to_remove.append(grid_to_agent.get((gx,gy)))
                did_remove = True
                
            # ----- RULE 4.1 - lone remnants decaying ---
            if not did_remove and len(emergence_agents) == 2 and neighbor_count == 0:
                if not to_remove:
                    to_remove.append(grid_to_agent.get((gx, gy)))
                    did_remove = True
                    
            # ----- RULE 5 - geometric completion ---
            is_part_of_square = any([           # check if the pixel part of a 2x2 block
                up and left and up_left,
                up and right and up_right,
                down and left and down_left,
                down and right and down_right
            ])
            
            # If we have an L-shape but no completion, build the diagonal
            if not is_part_of_square:
                if up and left: to_add.add((gx - 1, gy - 1))
                if up and right: to_add.add((gx + 1, gy - 1))
                if down and left: to_add.add((gx - 1, gy + 1))
                if down and right: to_add.add((gx + 1, gy + 1))
            
            # --- RULE 3 - movements (growth) ---
            if not did_remove and ((left and right) or (up and down)):
                # shift by adding 1 and deleting 1
                rx, ry = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                to_add.add((gx + rx, gy +ry))
                
                candidates = []
                if left and right:
                    candidates += [grid_to_agent.get((gx - 1, gy)), grid_to_agent.get((gx + 1, gy))]
                if up and down:
                    candidates += [grid_to_agent.get((gx, gy - 1)), grid_to_agent.get((gx, gy + 1))]
                                
                # Filter removal candidates to avoid breaking 2x2 Order blocks
                loose_candidates = [c for c in candidates if c is not None]
                if loose_candidates:
                    to_remove.append(random.choice(loose_candidates))
                    did_remove = True
                    
            if not did_remove:
                # --- RULE 1 - seeding ---
                if neighbor_count == 0:
                    dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                    to_add.add((gx + dx, gy + dy))
                    
                # --- RULE 2 - Branching ---
                if left ^ right:    # horizontal
                    to_add.add((gx, gy + random.choice([-1, 1])))
                if up ^ down:       # vertical
                    to_add.add((gx + random.choice([-1, 1]), gy))
        
        # deletion            
        if to_remove:
            remove_ids = {id(a) for a in to_remove if a is not None}
            emergence_agents = [a for a in emergence_agents if id(a) not in remove_ids]
        
        # refresh occupied
        occupied = set(to_grid(a) for a in emergence_agents)
        
        # growth
        for cell in to_add:
            if cell not in occupied:
                emergence_agents.append(
                    pygame.Vector2(cell[0]*cell_size, cell[1]*cell_size)
                )          

    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()