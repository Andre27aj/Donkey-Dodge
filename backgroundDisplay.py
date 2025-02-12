import pygame

pygame.init()

screen = pygame.display.set_mode((1792, 1024))

back = pygame.image.load("Back.png")
back = pygame.transform.scale(back, (1792, 1024))

carlo = pygame.image.load("Carlo.png")
carlo = pygame.transform.scale(carlo, (288, 288))

show_background = False
keys_pressed = []

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            keys_pressed.append(event.key)

            if keys_pressed[-2:] == [pygame.K_c, pygame.K_b]:
                show_background = True

    if show_background:
        screen.blit(carlo, (896, 512))
    else:
        screen.blit(back, (0, 0))

    pygame.display.flip()

pygame.quit()