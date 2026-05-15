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

def to_grid(pos):
    return (int(pos.x // cell_size), int(pos.y // cell_size))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill((0, 0, 0))
    
    # MAIN RENDER LOOP
    occupied = set()
    for agent in emergence_agents:
        pygame.draw.rect(screen, (255, 255, 255), (agent.x, agent.y, cell_size, cell_size))
        occupied.add(to_grid(agent))

    spawn_timer += 1

    if spawn_timer > 30:
        spawn_timer = 0
        
        to_add = set()
        to_remove = []
        
        # Optimization: Map grid positions to agents for O(1) lookups
        grid_to_agent = {to_grid(a): a for a in emergence_agents}

        # Rule execution population count is based on the snapshot at the start of the cycle
        current_pop = len(emergence_agents)

        for gx, gy in occupied:
            # --- FIXED 3x3 GRID SYSTEM ---
            # bx, by represent the block index (e.g., 0,0, 1,0, etc.)
            bx, by = gx // 3, gy // 3 
            
            # Fixed Neighbor Check: Only look at cells within the SAME 3x3 tile.
            # A pixel at the edge of a tile no longer "sees" pixels in the adjacent tile.
            def check_in_tile(nx, ny):
                if nx // 3 == bx and ny // 3 == by:
                    return (nx, ny) in occupied
                return False

            # We check all 8 neighbors within the fixed tile boundaries.
            up_left, up, up_right = check_in_tile(gx-1, gy-1), check_in_tile(gx, gy-1), check_in_tile(gx+1, gy-1)
            left,        right    = check_in_tile(gx-1, gy),                       check_in_tile(gx+1, gy)
            down_left, down, down_right = check_in_tile(gx-1, gy+1), check_in_tile(gx, gy+1), check_in_tile(gx+1, gy+1)
            
            # Position awareness within the fixed tile (0, 1, or 2)
            lx, ly = gx % 3, gy % 3
            is_corner = (lx in [0, 2]) and (ly in [0, 2])

            did_remove = False
            
            # --- RULE 4: DECAYING (Lone Remnants) --- 
            if current_pop == 2 and not (
                up_left or up or up_right or left or right or down_left or down or down_right
            ):
                if not to_remove:
                    to_remove.append(grid_to_agent.get((gx, gy)))
                    did_remove = True

            # --- RULE 3: STABILITY CONTROL (Triple Connection within Tile) ---
            if not did_remove and ((left and right) or (up and down)): 
                # 1. Add another pixel (random axis)
                rx, ry = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                to_add.add((gx + rx, gy + ry))

                # 2. Randomly remove one of the cardinal neighbors that triggered the rule
                candidates = []
                if left and right: candidates += [grid_to_agent.get((gx-1, gy)), grid_to_agent.get((gx+1, gy))]
                if up and down: candidates += [grid_to_agent.get((gx, gy-1)), grid_to_agent.get((gx, gy+1))]
                
                candidates = [c for c in candidates if c is not None]
                if candidates:
                    to_remove.append(random.choice(candidates))
                    did_remove = True
                    
            if not did_remove:
                # --- RULE 1: SEEDING (Isolated Pixel) ---
                if not (left or right or up or down):
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    to_add.add((gx + dx, gy + dy))

                # --- RULE 2: BRANCHING (Pair Endings) ---
                if left ^ right: # Horizontal pair end -> Grow vertically
                    to_add.add((gx, gy + random.choice([-1, 1])))

                if up ^ down: # Vertical pair end -> Grow horizontally
                    to_add.add((gx + random.choice([-1, 1]), gy))              
        
        # Apply changes
        if to_remove:
            remove_ids = {id(a) for a in to_remove}
            emergence_agents = [a for a in emergence_agents if id(a) not in remove_ids]
        
        occupied = set(to_grid(a) for a in emergence_agents)
        for cell in to_add:
            if cell not in occupied:
                emergence_agents.append(pygame.Vector2(cell[0]*cell_size, cell[1]*cell_size))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
