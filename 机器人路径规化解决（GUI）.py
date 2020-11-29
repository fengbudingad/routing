#机器人优化路径求解
#基于元胞自动机算法
#参考：Memory Puzzle，Slide Puzzle，Wormy

import pygame
import sys
import random
import numpy as py
from pygame.locals import *


#设置常量

#程序运行速率
FPS = 3000
#窗口尺寸、障碍物尺寸与数目
WINDOWWIDTH = 1020
WINDOWHEIGHT = 600
CELLSIZE = 20
CELLWIDTH = 45
CELLHEIGHT = 30
#Color    R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
BGCOLOR = BLACK
TITLECOLOR = GREEN
TEXTCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE
#字体大小
FONTSIZE = 25
#随机生成障碍数目
RANDOMNUMBER1 = 200
RANDOMNUMBER2 = 100


#图形交互界面函数部分

#绘制栅栏
def drawGrid():
    for x in range(0, WINDOWWIDTH - 5 * CELLSIZE, CELLSIZE):
        pygame.draw.line(D, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    x = WINDOWWIDTH - 6 * CELLSIZE
    pygame.draw.line(D, DARKGREEN, (x, 0), (x, WINDOWHEIGHT), 5)
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(D, DARKGRAY, (0, y), (WINDOWWIDTH - 6 * CELLSIZE, y))


#返回按钮的相关对象
def makeText(text, color, bgcolor, top, left):
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


#绘制障碍物
def drawwall(x, y):
    wallSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(D, DARKGREEN, wallSegmentRect)
    wallInner = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(D, GREEN, wallInner)
    FPSCLOCK.tick(FPS)


#绘制优化路径
def drawRoute(route):
    lenth = len(route)
    for i in range(lenth):
        cox = route[i][0]
        coy = route[i][1]
        wallSegmentRect = pygame.Rect((coy-1)*CELLSIZE, (cox-1)*CELLSIZE, CELLSIZE, CELLSIZE)
        pygame.draw.rect(D, BLUE, wallSegmentRect)
        wallInner = pygame.Rect((coy-1)*CELLSIZE+4, (cox-1)*CELLSIZE+4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(D, WHITE, wallInner)
    drawLengthOfRoute(route)
    pygame.display.update()
    #定义路径绘出后在屏幕上显示时间：
    pygame.time.wait(20000)
    FPSCLOCK.tick(FPS)
    

#将方格坐标转化为左上角的像素坐标
def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * CELLSIZE
    top = boxy * CELLSIZE
    return (left, top)


#得到窗口上一点所在的方格的坐标
def getBoxAtPixel(x, y):
    for boxx in range(CELLWIDTH):
        for boxy in range(CELLHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, CELLSIZE, CELLSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


#绘制方格的高亮蓝色边框
def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(D, HIGHLIGHTCOLOR, (left - 1, top - 1, CELLSIZE + 2, CELLSIZE + 2), 2)


#绘制按钮的高亮蓝色边框
def drawHighlightBoxs(rect):
    (left, top) = rect.topleft
    (right, bottom) = rect.bottomright
    pygame.draw.rect(D, HIGHLIGHTCOLOR, (left - 1, top - 1, right - left + 2, bottom - top + 2), 4)


#将所有的方格初始状态定义为没有障碍物
def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(CELLWIDTH):
        revealedBoxes.append([val] * CELLHEIGHT)
    return revealedBoxes


#在每次循环初始绘制面板
def drawBoard(revealed):
    drawGrid()
    for boxx in range(CELLWIDTH):
        for boxy in range(CELLHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if revealed[boxx][boxy]:
                drawwall(boxx * CELLSIZE, boxy * CELLSIZE)


#绘制按钮
def drawButton():
    D.blit(EXIT_SURF, EXIT_RECT)
    D.blit(RANDOM_1_SURF, RANDOM_1_RECT)
    D.blit(RANDOM_2_SURF, RANDOM_2_RECT)
    D.blit(RESET_SURF, RESET_RECT)
    D.blit(EXAMPLE_1_SURF, EXAMPLE_1_RECT)
    D.blit(EXAMPLE_2_SURF, EXAMPLE_2_RECT)
    D.blit(EXAMPLE_3_SURF, EXAMPLE_3_RECT)
    D.blit(EXAMPLE_4_SURF, EXAMPLE_4_RECT)
    D.blit(SOLVE_SURF, SOLVE_RECT)


#在窗口边缘显示路径长度
def drawLengthOfRoute(route):
    lenth=len(route)
    lengthSurf=BASICFONT.render('Length:%s'%(lenth),True,WHITE)
    lengthRect=lengthSurf.get_rect()
    lengthRect.topleft=(WINDOWWIDTH - 110,20)
    D.blit(lengthSurf,lengthRect)


#退出程序
def terminate():
    pygame.quit()
    sys.exit()


#元胞自动机优化路径算法函数部分

#避免机器人过度靠近障碍物设置的危险碰撞函数
def danger(maze):
    m = len(maze)
    n = len(maze[0])
    dangervalue = [[0 for i in range(n - 2)] for j in range(m - 2)]
    for i in range(1, m - 1):
        for j in range(1, n - 1):
            list1 = [maze[i][j - 1], maze[i - 1][j], maze[i][j + 1], maze[i + 1][j]]
            list2 = [maze[i - 1][j - 1], maze[i - 1][j + 1], maze[i + 1][j + 1], maze[i + 1][j - 1]]
            num1 = list1.count(1)
            num2 = list2.count(1)
            if num1 > 0:
                if num1 == 4:
                    dangervalue[i - 1][j - 1] = 2
                elif num1 == 3:
                    dangervalue[i - 1][j - 1] = 1.5
                elif num1 == 2:
                    if (maze[i][j - 1] == 1 and maze[i - 1][j] == 1) or (
                            maze[i - 1][j] == 1 and maze[i][j + 1] == 1) or (
                            maze[i][j + 1] == 1 and maze[i + 1][j] == 1) or (
                            maze[i + 1][j] == 1 and maze[i][j - 1] == 1):
                        dangervalue[i - 1][j - 1] = 1.2
                    else:
                        dangervalue[i - 1][j - 1] = 1
                else:
                    dangervalue[i - 1][j - 1] = 0.8
            elif num2 > 0:
                dangervalue[i - 1][j - 1] = 0.25 * num2
            else:
                dangervalue[i - 1][j - 1] = 0
    return dangervalue


#选取列表制定部分
def choose(list):
    l = len(list)
    i = 0
    list.sort(reverse=True)
    List = list.copy()
    while list.pop() < 3:
        i = i + 1
    return (List[l - i - 1])


#列表最大元素值
def max(list):
    list.sort(reverse=False)
    l = len(list)
    m = list[l - 1]
    return m


#列表最小元素值
def min(list):
    list.sort(reverse=True)
    l = len(list)
    m = list[l - 1]
    return m


#基于元胞自动机算法，定义元胞演化规则函数
def cell(maze):
    m = len(maze)
    n = len(maze[0])
    list1 = maze
    list2 = [[0 for i in range(n)] for j in range(m)]
    for i in range(0, m):
        for j in range(0, n):
            if list1[i][j] > 0:
                list2[i][j] = list1[i][j]
            elif j == 1:
                if i == 1:
                    if list1[i + 1][j + 1] >= 3:
                        list2[i][j] = list1[i + 1][j + 1] + 2
                    elif max([list1[i][j + 1], list1[i + 1][j]]) >= 3:
                        list = [list1[i][j + 1], list1[i + 1][j]]
                        list2[i][j] = choose(list) + 2
                    else:
                        list2[i][j] = list1[i][j]
                elif i == m - 2:
                    if list1[i - 1][j + 1] >= 3:
                        list2[i][j] = list1[i - 1][j + 1] + 2
                    elif max([list1[i - 1][j], list1[i][j + 1]]) >= 3:
                        list = [list1[i - 1][j], list1[i][j + 1]]
                        list2[i][j] = choose(list) + 2
                    else:
                        list2[i][j] = list1[i][j]
                else:
                    if max([list1[i - 1][j + 1], list1[i + 1][j + 1]]) >= 3:
                        if ((list1[i - 1][j + 1] >= 3) and list1[i - 1][j] == 1 and list1[i][j + 1] == 1) or (
                                (list1[i + 1][j + 1] >= 3) and list1[i][j + 1] == 1 and list1[i + 1][j] == 1):
                            list2[i][j] = list1[i][j]
                        else:
                            list = [list1[i - 1][j + 1], list1[i + 1][j + 1]]
                            list2[i][j] = choose(list) + 2
                    elif max([list1[i - 1][j], list1[i + 1][j], list1[i][j + 1]]) >= 3:
                        list = [list1[i - 1][j], list1[i + 1][j], list1[i][j + 1]]
                        list2[i][j] = choose(list) + 2
                    else:
                        list2[i][j] = list1[i][j]
            elif j == n - 2:
                if i == 1:
                    if list1[i + 1][j - 1] >= 3:
                        list2[i][j] = list1[i + 1][j - 1] + 2
                    elif max([list1[i][j - 1], list1[i+1][j ]]) >= 3:
                        list = [list1[i][j - 1], list1[i+1][j ]]
                        list2[i][j] = choose(list) + 2
                    else:
                        list2[i][j] = list1[i][j]
                elif i == m - 2:
                    list2[i][j] = list1[i][j]
                else:
                    if max([list1[i - 1][j - 1], list1[i + 1][j - 1]]) >= 3:
                        if ((list1[i - 1][j - 1] >= 3) and list1[i - 1][j] == 1 and list1[i][j - 1] == 1) or (
                                (list1[i + 1][j - 1] >= 3) and list1[i][j - 1] == 1 and list1[i + 1][j] == 1):
                            list2[i][j] = list1[i][j]
                        else:
                            list = [list1[i - 1][j - 1], list1[i + 1][j - 1]]
                            list2[i][j] = choose(list) + 2
                    elif max([list1[i - 1][j], list1[i + 1][j], list1[i][j - 1]]) >= 3:
                        list = [list1[i - 1][j], list1[i + 1][j], list1[i][j - 1]]
                        list2[i][j] = choose(list) + 2
                    else:
                        list2[i][j] = list1[i][j]
            elif i == 1:
                if max([list1[i + 1][j - 1], list1[i + 1][j + 1]]) >= 3:
                    if ((list1[i + 1][j - 1] >= 3) and list1[i][j - 1] == 1 and list1[i + 1][j] == 1) or (
                            (list1[i + 1][j + 1] >= 3) and list1[i + 1][j] == 1 and list1[i][j + 1] == 1):
                        list2[i][j] = list1[i][j]
                    else:
                        list = [list1[i + 1][j - 1], list1[i + 1][j + 1]]
                        list2[i][j] = choose(list) + 2
                elif max([list1[i][j - 1], list1[i][j + 1], list1[i][j + 1]]) >= 3:
                    list = [list1[i][j - 1], list1[i][j + 1], list1[i][j + 1]]
                    list2[i][j] = choose(list) + 2
                else:
                    list2[i][j] = list1[i][j]
            elif i == m - 2:
                if max([list1[i - 1][j - 1], list1[i - 1][j + 1]]) >= 3:
                    if ((list1[i - 1][j - 1] >= 3) and list1[i][j - 1] == 1 and list1[i - 1][j] == 1) or (
                            (list1[i - 1][j + 1] >= 3) and list1[i - 1][j] == 1 and list1[i][j + 1] == 1):
                        list2[i][j] = list1[i][j]
                    else:
                        list = [list1[i - 1][j - 1], list1[i - 1][j + 1]]
                        list2[i][j] = choose(list) + 2
                elif max([list1[i][j - 1], list1[i][j + 1], list1[i - 1][j]]) >= 3:
                    list = [list1[i][j - 1], list1[i][j + 1], list1[i - 1][j]]
                    list2[i][j] = choose(list) + 2
                else:
                    list2[i][j] = list1[i][j]
            else:
                if max([list1[i - 1][j - 1], list1[i - 1][j + 1], list1[i + 1][j + 1], list1[i + 1][j - 1]]) >= 3:
                    if ((list1[i + 1][j - 1] >= 3) and list1[i][j - 1] == 1 and list1[i + 1][j] == 1) or (
                            (list1[i + 1][j + 1] >= 3) and list1[i + 1][j] == 1 and list1[i][j + 1] == 1) \
                            or ((list1[i - 1][j + 1] >= 3) and list1[i - 1][j] == 1 and list1[i][j + 1] == 1) or \
                            ((list1[i-1][j-1]>=3) and list1[i-1][j]==1 and list1[i][j-1]==1):
                        list2[i][j] = list1[i][j]
                    else:
                        list = [list1[i - 1][j - 1], list1[i - 1][j + 1], list1[i + 1][j + 1], list1[i + 1][j - 1]]
                        list2[i][j] = choose(list) + 2
                elif max([list1[i][j - 1], list1[i - 1][j], list1[i + 1][j], list1[i][j + 1]]) >= 3:
                    list = [list1[i][j - 1], list1[i - 1][j], list1[i + 1][j], list1[i][j + 1]]
                    list2[i][j] = choose(list) + 2
                else:
                    list2[i][j] = list1[i][j]
    return list2


#对路径进行修剪
def shoove(list):
    lenth=len(list)
    for i in range(lenth-3):
        try:
            condition=((list[i][0]-list[i+1][0])**2+(list[i][1]-list[i+1][1])**2)==1 and ((list[i+2][0]-list[i+1][0])**2+(list[i+2][1]-list[i+1][1])**2)==1\
            and ((list[i+3][0]-list[i+2][0])**2+(list[i+3][1]-list[i+2][1])**2)==1 and ((list[i+3][0]-list[i][0])**2+(list[i+3][1]-list[i][1])**2)==1
            if condition == True:
                list.remove(list[i + 1])
                list.remove(list[i + 2])
        except:
            print('抱歉，此问题无法解决!!','1')
            terminate()
    return list


#删除往返路径
def shorten(list):
    lenth = len(list)
    for i in range(lenth):
        try:
            for j in range(i,lenth):
                if list[i]==list[j]:
                    for k in range(i,j):
                        list.remove(list[k])
                        lenth = len(list)
        except:
            print('抱歉，此问题无法解决!!','2')
            terminate()
    return list

    
#根据终态各元胞的值确定机器人优化路径
def path(list):
    maze = list.copy()
    m = len(maze)
    n = len(maze[0])
    row = 1
    col = 1
    Path = [[1, 1]]
    i = 0
    try:
        while maze[row + 1][col + 1] != 3 and maze[row][col + 1] != 3 and maze[row + 1][col] != 3:
            list1 = [maze[row + 1][col - 1], maze[row + 1][col], maze[row + 1][col + 1], maze[row][col + 1],
                     maze[row - 1][col + 1],maze[row][col - 1], maze[row - 1][col], maze[row - 1][col - 1]]
            list2 = [maze[row + 1][col - 1], maze[row + 1][col], maze[row + 1][col + 1], maze[row][col + 1],
                     maze[row - 1][col + 1]]
            number=list1.count(1)
            while 1 in list1:
                list1.remove(1)
            while 4 in list1:
                list1.remove(4)
            while 1 in list2:
                list2.remove(1)
            while 4 in list2:
                list2.remove(4)
            if number>=3:
                if (min(list1) == maze[row][col + 1] or min(list1) == maze[row + 1][col]) and min(list1) > 4:
                    if min(list1) == maze[row][col + 1]:
                        Path.append([row, col + 1])
                    else:
                        Path.append([row + 1, col])
                elif (min(list1) == maze[row + 1][col + 1]) and min(list1) > 4:
                    Path.append([row + 1, col + 1])
                elif (min(list1) == maze[row - 1][col + 1] or min(list1) == maze[row + 1][col - 1]) and min(list1) > 4:
                    if min(list1) == maze[row - 1][col + 1]:
                        Path.append([row - 1, col + 1])
                    else:
                        Path.append([row + 1, col - 1])
                elif (min(list1)==maze[row-1][col] or min(list1)==maze[row][col-1]) and min(list1)>4:
                    if min(list1)==maze[row-1][col]:
                        Path.append([row-1,col])
                    else:
                        Path.append([row,col-1])
                else:
                    Path.append([row-1,col-1])
            else:
                if (min(list2) == maze[row][col + 1] or min(list2) == maze[row + 1][col]) and min(list2) > 4:
                    if min(list2) == maze[row][col + 1]:
                        Path.append([row, col + 1])
                    else:
                        Path.append([row + 1, col])
                elif (min(list2) == maze[row + 1][col + 1]) and min(list2) > 4:
                    Path.append([row + 1, col + 1])
                elif (min(list2) == maze[row - 1][col + 1] or min(list2) == maze[row + 1][col - 1]) and min(list2) > 4:
                    if min(list2) == maze[row - 1][col + 1]:
                        Path.append([row - 1, col + 1])
                    else:
                        Path.append([row + 1, col - 1])
            i = i + 1
            maze[row][col] = 1000000
            [row, col] = Path[i]
    except:
        print('抱歉，此问题无法解决!!','4')
        #terminate()
    Path.append([m - 2, n - 2])#初步确定路径

    #对路径进行修饰，减少弯折,进一步优化路径
    Path=shorten(Path)
    while shoove(Path)!=Path:
        Path=shoove(Path)
    lenth=len(Path)
    for i in range(lenth-3):
        condition1=((Path[i][0]-Path[i+1][0])**2+(Path[i][1]-Path[i+1][1])**2)==1 and ((Path[i+2][0]-Path[i+1][0])**2+(Path[i+2][1]-Path[i+1][1])**2)==1\
        and ((Path[i][0]-Path[i+2][0])**2+(Path[i][1]-Path[i+2][1])**2)==2
        condition2=((Path[i][0]-Path[i+1][0])**2+(Path[i][1]-Path[i+1][1])**2)==2 and ((Path[i+2][0]-Path[i+1][0])**2+(Path[i+2][1]-Path[i+1][1])**2)==2\
        and ((Path[i][0]-Path[i+2][0])**2+(Path[i][1]-Path[i+2][1])**2)==4
        condition3=((Path[i][0]-Path[i+1][0])**2+(Path[i][1]-Path[i+1][1])**2)==2 and ((Path[i+2][0]-Path[i+1][0])**2+(Path[i+2][1]-Path[i+1][1])**2)==1\
        and ((Path[i][0]-Path[i+2][0])**2+(Path[i][1]-Path[i+2][1])**2)==1
        condition4=((Path[i][0]-Path[i+1][0])**2+(Path[i][1]-Path[i+1][1])**2)==1 and ((Path[i+2][0]-Path[i+1][0])**2+(Path[i+2][1]-Path[i+1][1])**2)==2\
        and ((Path[i][0]-Path[i+2][0])**2+(Path[i][1]-Path[i+2][1])**2)==1
        midpointx=int((Path[i][0]+Path[i+2][0])/2)
        midpointy=int((Path[i][1]+Path[i+2][1])/2)
        if condition1==True:
            Path.remove(Path[i+1])
        if condition2==True and maze[midpointx][midpointy]!=1:
            Path[i+1]=[midpointx,midpointy]
        if condition3==True:
            Path.remove(Path[i+1])
        if condition4 == True:
            Path.remove(Path[i+1])
    return Path


#将交互界面产生的障碍物状态传递给算法函数作为元胞演化的初始态
def Solve(wallCoords):
    n = CELLWIDTH + 2
    m = CELLHEIGHT + 2
    maze = [[0 for i in range(n)] for j in range(m)]
    for coord in wallCoords:
        x = coord['x']
        y = coord['y']
        maze[y + 1][x + 1] = 1
    for i in range(m):
        maze[i][0] = 4
        maze[i][n - 1] = 4
    for j in range(n):
        maze[0][j] = 4
        maze[m - 1][j] = 4
    maze[1][1] = 2
    maze[m - 2][n - 2] = 3
    Cell = maze.copy()
    sys.setrecursionlimit(10000)
    Maze = maze.copy()
    maze2 = maze.copy()
    D = danger(maze)
    while cell(maze) != maze:
        maze = cell(maze)
    M = maze
    grad = M.copy()
    Array = py.array(grad)
    Array = Array.flatten()
    list1 = Array.tolist()
    while 0 in list1:
        x = list1.index(0)
        row = int(x / n)
        col = x % n
        if col == 0:
            row = row - 1
            col = n - 1
        Max = max([M[row + 1][col + 1], M[row + 1][col], M[row + 1][col - 1], M[row][col - 1], M[row - 1][col - 1],
                   M[row - 1][col], M[row - 1][col + 1], M[row][col + 1]])
        M[row][col] = Max +8
        list1[x] = 1
    for i in range(m):
        for j in range(n):
            if Maze[i][j] != 0:
                M[i][j] = Maze[i][j]
            else:
                M[i][j] = M[i][j] + D[i - 1][j - 1]
    route = path(M)
    lenth = len(route)
    return route




#主函数部分

global FPSCLOCK, D
pygame.init()
FPSCLOCK = pygame.time.Clock()
D = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
mousex = 0
mousey = 0
pygame.display.set_caption('机器人路径规划(起点在左上角，终点在右下角,点击添加障碍物，再次点击消除障碍物,单击右侧按钮实现相应功能，右上角显示路径长度)')
BASICFONT = pygame.font.SysFont('arial', FONTSIZE)
#建立按钮
EXAMPLE_1_SURF, EXAMPLE_1_RECT = makeText(' Example1', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 450)
EXAMPLE_2_SURF, EXAMPLE_2_RECT = makeText(' Example2', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 400)
EXAMPLE_3_SURF, EXAMPLE_3_RECT = makeText(' Example3', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 350)
EXAMPLE_4_SURF, EXAMPLE_4_RECT = makeText(' Example4', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 300)
RANDOM_1_SURF, RANDOM_1_RECT = makeText(' Random1', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 250)
RANDOM_2_SURF, RANDOM_2_RECT = makeText(' Random2', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 200)
RESET_SURF, RESET_RECT = makeText(' Reset ', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 150)
SOLVE_SURF, SOLVE_RECT = makeText(' Solve ', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 100)
EXIT_SURF, EXIT_RECT = makeText(' Exit ', TEXTCOLOR, TITLECOLOR, WINDOWWIDTH - 100, WINDOWHEIGHT - 50)
revealedBoxes = generateRevealedBoxesData(False)
wallCoords = []

while True:
    mouseClicked = False
    D.fill(BGCOLOR)
    drawBoard(revealedBoxes)
    drawGrid()
    drawButton()

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        #得到鼠标对应的坐标
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            mouseClicked = True

    boxx, boxy = getBoxAtPixel(mousex, mousey)

    #鼠标光标指在栅栏右侧：
    if boxx == None and boxy == None:
        #点中Reset按钮，清空所有已绘制的障碍物
        if RESET_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(RESET_RECT)
            if mouseClicked:
                wallCoords.clear()
                revealedBoxes = generateRevealedBoxesData(False)
        #建立两个疏密程度不同的随机房间实例
        elif RANDOM_1_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(RANDOM_1_RECT)
            if mouseClicked:
                for i in range(RANDOMNUMBER1):
                    startx = random.randint(0, CELLWIDTH - 1)
                    starty = random.randint(0, CELLHEIGHT - 1)
                    if {'x': startx, 'y': starty} not in wallCoords and (startx, starty) != (0, 0):
                        wallCoords.append({'x': startx, 'y': starty})
                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    #绘制障碍物后及时改变方格状态，否则障碍物图像不能长久存在：
                    revealedBoxes[coord['x']][coord['y']] = True

        elif RANDOM_2_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(RANDOM_2_RECT)
            if mouseClicked:
                for i in range(RANDOMNUMBER2):
                    startx = random.randint(0, CELLWIDTH - 1)
                    starty = random.randint(0, CELLHEIGHT - 1)
                    if {'x': startx, 'y': starty} not in wallCoords and (startx, starty) != (0, 0):
                        wallCoords.append({'x': startx, 'y': starty})
                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    revealedBoxes[coord['x']][coord['y']] = True
        #点中Solve按钮，显示优化路径
        elif SOLVE_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(SOLVE_RECT)
            if mouseClicked:
                route = Solve(wallCoords)
                pygame.display.update()
                drawRoute(route)
                print('障碍物坐标为:')
                print(wallCoords)
                print("机器人优化路径为：")
                lenth = len(route)
                for i in range(lenth):
                    cox = route[i][0]
                    coy = route[i][1]
                    print("-->(%d,%d)" % (cox, coy))
                print("路径长度为：%d"%lenth)
        #点中Exit按钮，退出程序
        elif EXIT_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(EXIT_RECT)
            if mouseClicked:
                terminate()
        #建立四个房间实例
        elif EXAMPLE_1_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(EXAMPLE_1_RECT)
            if mouseClicked:
                wallCoords = [{'x': 11, 'y': 11}, {'x': 11, 'y': 15}, {'x': 11, 'y': 14}, {'x': 11, 'y': 13},
                              {'x': 11, 'y': 12}, \
                              {'x': 11, 'y': 10}, {'x': 11, 'y': 9}, {'x': 11, 'y': 8}, {'x': 11, 'y': 7},
                              {'x': 11, 'y': 6}, {'x': 11, 'y': 5}, {'x': 11, 'y': 4}, {'x': 11, 'y': 3}, \
                              {'x': 11, 'y': 2}, {'x': 11, 'y': 1}, {'x': 10, 'y': 16}, {'x': 9, 'y': 16},
                              {'x': 8, 'y': 16}, {'x': 7, 'y': 16}, {'x': 6, 'y': 16}, {'x': 5, 'y': 16},
                              {'x': 4, 'y': 16}, \
                              {'x': 3, 'y': 16}, {'x': 2, 'y': 16}, {'x': 1, 'y': 16}]
                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    revealedBoxes[coord['x']][coord['y']] = True

        elif EXAMPLE_2_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(EXAMPLE_2_RECT)
            if mouseClicked:
                wallCoords=[{'x': 11, 'y': 11}, {'x': 11, 'y': 15}, {'x': 11, 'y': 14}, {'x': 11, 'y': 13}, \
                            {'x': 11, 'y': 12}, {'x': 11, 'y': 10}, {'x': 11, 'y': 9}, {'x': 11, 'y': 8},\
                            {'x': 11, 'y': 7}, {'x': 11, 'y': 6}, {'x': 11, 'y': 5}, {'x': 11, 'y': 4},\
                            {'x': 11, 'y': 3}, {'x': 11, 'y': 2}, {'x': 11, 'y': 1}, {'x': 10, 'y': 16},\
                            {'x': 9, 'y': 16}, {'x': 8, 'y': 16}, {'x': 7, 'y': 16}, {'x': 6, 'y': 16},\
                            {'x': 5, 'y': 16}, {'x': 4, 'y': 16}, {'x': 3, 'y': 16}, {'x': 2, 'y': 16},\
                            {'x': 1, 'y': 16}, {'x': 11, 'y': 0}, {'x': 0, 'y': 20}, {'x': 1, 'y': 20},\
                            {'x': 2, 'y': 20}, {'x': 3, 'y': 20}, {'x': 4, 'y': 20}, {'x': 5, 'y': 20},\
                            {'x': 6, 'y': 20}, {'x': 7, 'y': 20}, {'x': 8, 'y': 20}, {'x': 9, 'y': 20},\
                            {'x': 10, 'y': 20}, {'x': 11, 'y': 20}, {'x': 12, 'y': 19}, {'x': 13, 'y': 18}, \
                            {'x': 14, 'y': 17}, {'x': 15, 'y': 16}, {'x': 15, 'y': 15}, {'x': 15, 'y': 14}, \
                            {'x': 15, 'y': 13}, {'x': 15, 'y': 12}, {'x': 15, 'y': 11}, {'x': 15, 'y': 10},\
                            {'x': 15, 'y': 9}, {'x': 15, 'y': 8}, {'x': 15, 'y': 7}, {'x': 15, 'y': 6},\
                            {'x': 15, 'y': 5}, {'x': 15, 'y': 4}, {'x': 15, 'y': 3}, {'x': 15, 'y': 2},\
                            {'x': 20, 'y': 0}, {'x': 20, 'y': 1}, {'x': 20, 'y': 2}, {'x': 20, 'y': 3},\
                            {'x': 20, 'y': 5}, {'x': 20, 'y': 4}, {'x': 20, 'y': 6}, {'x': 20, 'y': 7}, \
                            {'x': 20, 'y': 8}, {'x': 20, 'y': 10}, {'x': 20, 'y': 9}, {'x': 20, 'y': 11},\
                            {'x': 20, 'y': 12}, {'x': 20, 'y': 13}, {'x': 20, 'y': 14}, {'x': 20, 'y': 15},\
                            {'x': 20, 'y': 16}, {'x': 20, 'y': 17}, {'x': 20, 'y': 18}, {'x': 20, 'y': 19}, \
                            {'x': 20, 'y': 20}, {'x': 19, 'y': 21}, {'x': 18, 'y': 22}, {'x': 17, 'y': 23},\
                            {'x': 16, 'y': 24}, {'x': 15, 'y': 24}, {'x': 14, 'y': 24}, {'x': 13, 'y': 24},\
                            {'x': 12, 'y': 24}, {'x': 11, 'y': 24}, {'x': 10, 'y': 24}, {'x': 8, 'y': 24}, \
                            {'x': 9, 'y': 24}, {'x': 7, 'y': 24}, {'x': 6, 'y': 24}, {'x': 4, 'y': 24},\
                            {'x': 3, 'y': 24}, {'x': 2, 'y': 24}, {'x': 5, 'y': 24}, {'x': 2, 'y': 25},\
                            {'x': 2, 'y': 26}, {'x': 6, 'y': 29}, {'x': 6, 'y': 28}, {'x': 6, 'y': 27}, \
                            {'x': 6, 'y': 26}, {'x': 11, 'y': 25}, {'x': 11, 'y': 26}, {'x': 11, 'y': 27}, \
                            {'x': 16, 'y': 29}, {'x': 16, 'y': 28}, {'x': 16, 'y': 27}, {'x': 16, 'y': 26},\
                            {'x': 17, 'y': 27}, {'x': 18, 'y': 26}, {'x': 19, 'y': 25}, {'x': 20, 'y': 24},\
                            {'x': 21, 'y': 23}, {'x': 22, 'y': 22}, {'x': 23, 'y': 21}, {'x': 24, 'y': 20},\
                            {'x': 24, 'y': 19}, {'x': 24, 'y': 18}, {'x': 24, 'y': 16}, {'x': 24, 'y': 17},\
                            {'x': 24, 'y': 15}, {'x': 24, 'y': 14}, {'x': 24, 'y': 13}, {'x': 24, 'y': 12},\
                            {'x': 24, 'y': 11}, {'x': 24, 'y': 10}, {'x': 24, 'y': 9}, {'x': 24, 'y': 8},\
                            {'x': 24, 'y': 6}, {'x': 24, 'y': 7}, {'x': 24, 'y': 5}, {'x': 24, 'y': 4}, \
                            {'x': 24, 'y': 3}, {'x': 24, 'y': 2}, {'x': 24, 'y': 1}, {'x': 28, 'y': 0}, \
                            {'x': 28, 'y': 1}, {'x': 28, 'y': 2}, {'x': 28, 'y': 3}, {'x': 28, 'y': 4},\
                            {'x': 28, 'y': 5}, {'x': 28, 'y': 6}, {'x': 28, 'y': 7}, {'x': 28, 'y': 8}, \
                            {'x': 28, 'y': 9}, {'x': 28, 'y': 10}, {'x': 28, 'y': 11}, {'x': 28, 'y': 12}, \
                            {'x': 28, 'y': 13}, {'x': 28, 'y': 14}, {'x': 28, 'y': 15}, {'x': 28, 'y': 16},\
                            {'x': 28, 'y': 17}, {'x': 28, 'y': 18}, {'x': 28, 'y': 19}, {'x': 28, 'y': 20},\
                            {'x': 28, 'y': 21}, {'x': 28, 'y': 22}, {'x': 28, 'y': 23}, {'x': 27, 'y': 24}, \
                            {'x': 26, 'y': 25}, {'x': 25, 'y': 26}, {'x': 24, 'y': 27}, {'x': 23, 'y': 28}, \
                            {'x': 33, 'y': 29}, {'x': 33, 'y': 28}, {'x': 33, 'y': 27}, {'x': 33, 'y': 26},\
                            {'x': 33, 'y': 25}, {'x': 33, 'y': 24}, {'x': 33, 'y': 23}, {'x': 33, 'y': 22}, \
                            {'x': 33, 'y': 21}, {'x': 33, 'y': 20}, {'x': 33, 'y': 19}, {'x': 33, 'y': 17},\
                            {'x': 33, 'y': 18}, {'x': 33, 'y': 16}, {'x': 33, 'y': 15}, {'x': 33, 'y': 14}, \
                            {'x': 33, 'y': 13}, {'x': 33, 'y': 11}, {'x': 33, 'y': 12}, {'x': 33, 'y': 10},\
                            {'x': 33, 'y': 9}, {'x': 33, 'y': 8}, {'x': 33, 'y': 7}, {'x': 33, 'y': 5}, \
                            {'x': 33, 'y': 6}, {'x': 33, 'y': 4}, {'x': 33, 'y': 3}, {'x': 34, 'y': 2},\
                            {'x': 35, 'y': 2}, {'x': 36, 'y': 2}, {'x': 37, 'y': 2}, {'x': 38, 'y': 2},\
                            {'x': 39, 'y': 2}, {'x': 40, 'y': 2}, {'x': 41, 'y': 2}, {'x': 42, 'y': 2},\
                            {'x': 42, 'y': 3}, {'x': 42, 'y': 4}, {'x': 42, 'y': 5}, {'x': 42, 'y': 6},\
                            {'x': 42, 'y': 7}, {'x': 44, 'y': 10}, {'x': 43, 'y': 11}, {'x': 42, 'y': 12},\
                            {'x': 41, 'y': 8}, {'x': 40, 'y': 9}]
                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    revealedBoxes[coord['x']][coord['y']] = True

        elif EXAMPLE_3_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(EXAMPLE_3_RECT)
            if mouseClicked:
                wallCoords = [{'x': 9, 'y': 0}, {'x': 8, 'y': 1}, {'x': 7, 'y': 2}, {'x': 5, 'y': 4}, \
                              {'x': 3, 'y': 6}, {'x': 2, 'y': 7}, {'x': 1, 'y': 8}, {'x': 1, 'y': 10}, \
                              {'x': 1, 'y': 12}, {'x': 1, 'y': 14}, {'x': 1, 'y': 16}, {'x': 1, 'y': 17}, \
                              {'x': 1, 'y': 19}, {'x': 1, 'y': 20}, {'x': 1, 'y': 21}, {'x': 1, 'y': 23}, \
                              {'x': 1, 'y': 24}, {'x': 1, 'y': 26}, {'x': 1, 'y': 27}, {'x': 3, 'y': 8}, \
                              {'x': 4, 'y': 8}, {'x': 6, 'y': 8}, {'x': 8, 'y': 8}, {'x': 10, 'y': 8}, \
                              {'x': 12, 'y': 8}, {'x': 13, 'y': 14}, {'x': 13, 'y': 16}, {'x': 13, 'y': 17}, \
                              {'x': 13, 'y': 18}, {'x': 13, 'y': 19}, {'x': 13, 'y': 21}, \
                              {'x': 13, 'y': 22}, {'x': 13, 'y': 23}, {'x': 13, 'y': 25}, {'x': 13, 'y': 26}, \
                              {'x': 13, 'y': 27}, {'x': 13, 'y': 28}, {'x': 12, 'y': 27}, \
                              {'x': 11, 'y': 27}, {'x': 10, 'y': 27}, {'x': 8, 'y': 27}, {'x': 7, 'y': 27}, \
                              {'x': 6, 'y': 27}, {'x': 4, 'y': 27}, {'x': 3, 'y': 27}, \
                              {'x': 3, 'y': 14}, {'x': 6, 'y': 14}, {'x': 8, 'y': 14}, {'x': 9, 'y': 14}, \
                              {'x': 11, 'y': 14}, {'x': 3, 'y': 21}, {'x': 5, 'y': 21}, \
                              {'x': 6, 'y': 21}, {'x': 8, 'y': 21}, {'x': 9, 'y': 21}, {'x': 10, 'y': 21}, \
                              {'x': 11, 'y': 21}, {'x': 17, 'y': 0}, {'x': 19, 'y': 0}, \
                              {'x': 20, 'y': 0}, {'x': 21, 'y': 0}, {'x': 23, 'y': 0}, {'x': 25, 'y': 0}, \
                              {'x': 26, 'y': 0}, {'x': 12, 'y': 3}, {'x': 14, 'y': 3}, \
                              {'x': 15, 'y': 3}, {'x': 16, 'y': 3}, {'x': 17, 'y': 3}, {'x': 19, 'y': 3}, \
                              {'x': 21, 'y': 3}, {'x': 23, 'y': 3}, {'x': 25, 'y': 3}, \
                              {'x': 27, 'y': 3}, {'x': 29, 'y': 3}, {'x': 19, 'y': 4}, {'x': 19, 'y': 5}, \
                              {'x': 18, 'y': 6}, {'x': 16, 'y': 8}, {'x': 15, 'y': 9}, \
                              {'x': 14, 'y': 11}, {'x': 15, 'y': 11}, {'x': 17, 'y': 11}, {'x': 19, 'y': 11}, \
                              {'x': 20, 'y': 11}, {'x': 22, 'y': 11}, {'x': 23, 'y': 11}, \
                              {'x': 24, 'y': 11}, {'x': 25, 'y': 11}, {'x': 23, 'y': 8}, {'x': 22, 'y': 7}, \
                              {'x': 25, 'y': 10}, {'x': 26, 'y': 11}, {'x': 27, 'y': 12}, \
                              {'x': 27, 'y': 13}, {'x': 12, 'y': 11}, {'x': 13, 'y': 13}, {'x': 12, 'y': 9}, \
                              {'x': 27, 'y': 7}, {'x': 28, 'y': 6}, {'x': 30, 'y': 5}, \
                              {'x': 31, 'y': 4}, {'x': 33, 'y': 3}, {'x': 35, 'y': 3}, {'x': 36, 'y': 3}, \
                              {'x': 39, 'y': 3}, {'x': 40, 'y': 3}, {'x': 41, 'y': 5}, \
                              {'x': 41, 'y': 8}, {'x': 41, 'y': 10}, {'x': 41, 'y': 11}, {'x': 41, 'y': 12}, \
                              {'x': 40, 'y': 12}, {'x': 38, 'y': 10}, {'x': 37, 'y': 9}, \
                              {'x': 35, 'y': 0}, {'x': 34, 'y': 3}, {'x': 35, 'y': 2}, {'x': 33, 'y': 5}, \
                              {'x': 33, 'y': 7}, {'x': 32, 'y': 8}, {'x': 31, 'y': 10}, \
                              {'x': 30, 'y': 12}, {'x': 25, 'y': 16}, {'x': 24, 'y': 17}, {'x': 21, 'y': 19}, \
                              {'x': 20, 'y': 20}, {'x': 18, 'y': 21}, {'x': 17, 'y': 22}, \
                              {'x': 16, 'y': 23}, {'x': 23, 'y': 20}, {'x': 23, 'y': 19}, {'x': 23, 'y': 22}, \
                              {'x': 23, 'y': 24}, {'x': 23, 'y': 25}, {'x': 23, 'y': 26}, \
                              {'x': 23, 'y': 28}, {'x': 37, 'y': 15}, {'x': 35, 'y': 17}, {'x': 34, 'y': 18}, \
                              {'x': 32, 'y': 20}, {'x': 31, 'y': 20}, {'x': 30, 'y': 21}, \
                              {'x': 28, 'y': 15}, {'x': 28, 'y': 18}, {'x': 28, 'y': 19}, {'x': 28, 'y': 21}, \
                              {'x': 28, 'y': 22}, {'x': 28, 'y': 25}, {'x': 28, 'y': 26}, \
                              {'x': 29, 'y': 27}, {'x': 30, 'y': 28}, {'x': 33, 'y': 28}, {'x': 28, 'y': 17}, \
                              {'x': 28, 'y': 16}, {'x': 40, 'y': 19}, {'x': 40, 'y': 20}, \
                              {'x': 32, 'y': 28}, {'x': 35, 'y': 28}, {'x': 36, 'y': 28}, {'x': 38, 'y': 28}, \
                              {'x': 39, 'y': 27}, {'x': 40, 'y': 26}, {'x': 40, 'y': 25}, \
                              {'x': 40, 'y': 22}, {'x': 40, 'y': 21}, {'x': 40, 'y': 23}, {'x': 40, 'y': 24}]
                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    revealedBoxes[coord['x']][coord['y']] = True

        elif EXAMPLE_4_RECT.collidepoint(mousex, mousey):
            drawHighlightBoxs(EXAMPLE_4_RECT)
            if mouseClicked:
                wallCoords = [{'x': 0, 'y': 1}, {'x': 0, 'y': 2}, {'x': 0, 'y': 3}, {'x': 0, 'y': 4}, \
                              {'x': 0, 'y': 5}, {'x': 0, 'y': 6}, {'x': 0, 'y': 7}, \
                              {'x': 0, 'y': 8}, {'x': 0, 'y': 9}, {'x': 0, 'y': 10}, {'x': 0, 'y': 11}, \
                              {'x': 0, 'y': 12}, {'x': 0, 'y': 13}, {'x': 0, 'y': 14}, \
                              {'x': 0, 'y': 15}, {'x': 0, 'y': 16}, {'x': 0, 'y': 17}, {'x': 0, 'y': 18}, \
                              {'x': 0, 'y': 19}, {'x': 0, 'y': 20}, {'x': 0, 'y': 21}, \
                              {'x': 0, 'y': 22}, {'x': 0, 'y': 23}, {'x': 0, 'y': 24}, {'x': 0, 'y': 25}, \
                              {'x': 0, 'y': 26}, {'x': 0, 'y': 27}, {'x': 0, 'y': 28}, \
                              {'x': 0, 'y': 29}, {'x': 2, 'y': 0}, {'x': 3, 'y': 0}, {'x': 4, 'y': 0}, \
                              {'x': 5, 'y': 0}, {'x': 6, 'y': 0}, {'x': 7, 'y': 1}, \
                              {'x': 8, 'y': 2}, {'x': 8, 'y': 3}, {'x': 8, 'y': 4}, {'x': 8, 'y': 5}, \
                              {'x': 8, 'y': 6}, {'x': 8, 'y': 7}, {'x': 8, 'y': 8}, \
                              {'x': 8, 'y': 9}, {'x': 8, 'y': 10}, {'x': 7, 'y': 11}, {'x': 6, 'y': 12}, \
                              {'x': 5, 'y': 13}, {'x': 3, 'y': 14}, {'x': 2, 'y': 14}, \
                              {'x': 4, 'y': 15}, {'x': 5, 'y': 16}, {'x': 6, 'y': 17}, {'x': 7, 'y': 18}, \
                              {'x': 8, 'y': 20}, {'x': 8, 'y': 21}, {'x': 8, 'y': 23}, \
                              {'x': 8, 'y': 24}, {'x': 8, 'y': 25}, {'x': 8, 'y': 27}, {'x': 8, 'y': 28}, \
                              {'x': 8, 'y': 29}, {'x': 12, 'y': 0}, {'x': 13, 'y': 0}, \
                              {'x': 14, 'y': 0}, {'x': 15, 'y': 0}, {'x': 11, 'y': 1}, {'x': 10, 'y': 2}, \
                              {'x': 10, 'y': 3}, {'x': 10, 'y': 4}, {'x': 10, 'y': 6}, \
                              {'x': 10, 'y': 7}, {'x': 10, 'y': 8}, {'x': 10, 'y': 10}, {'x': 10, 'y': 11}, \
                              {'x': 10, 'y': 13}, {'x': 10, 'y': 15}, {'x': 10, 'y': 16}, \
                              {'x': 10, 'y': 19}, {'x': 10, 'y': 20}, {'x': 10, 'y': 23}, {'x': 10, 'y': 24}, \
                              {'x': 10, 'y': 26}, {'x': 10, 'y': 27}, {'x': 11, 'y': 28}, \
                              {'x': 12, 'y': 29}, {'x': 13, 'y': 29}, {'x': 14, 'y': 29}, {'x': 16, 'y': 28}, \
                              {'x': 17, 'y': 27}, {'x': 17, 'y': 26}, {'x': 17, 'y': 25}, \
                              {'x': 17, 'y': 24}, {'x': 17, 'y': 22}, {'x': 17, 'y': 20}, {'x': 17, 'y': 17}, \
                              {'x': 17, 'y': 15}, {'x': 17, 'y': 13}, {'x': 17, 'y': 11}, \
                              {'x': 17, 'y': 9}, {'x': 17, 'y': 7}, {'x': 17, 'y': 5}, {'x': 17, 'y': 3}, \
                              {'x': 16, 'y': 1}, {'x': 17, 'y': 2}, {'x': 19, 'y': 0}, \
                              {'x': 19, 'y': 1}, {'x': 19, 'y': 3}, {'x': 19, 'y': 4}, {'x': 19, 'y': 6}, \
                              {'x': 19, 'y': 8}, {'x': 19, 'y': 9}, {'x': 19, 'y': 11}, \
                              {'x': 19, 'y': 14}, {'x': 19, 'y': 15}, {'x': 19, 'y': 16}, {'x': 19, 'y': 17}, \
                              {'x': 19, 'y': 19}, {'x': 19, 'y': 20}, \
                              {'x': 19, 'y': 21}, {'x': 19, 'y': 24}, {'x': 19, 'y': 26}, {'x': 19, 'y': 27}, \
                              {'x': 19, 'y': 28}, {'x': 19, 'y': 29}, \
                              {'x': 20, 'y': 0}, {'x': 21, 'y': 0}, {'x': 22, 'y': 0}, {'x': 23, 'y': 0}, \
                              {'x': 24, 'y': 0}, {'x': 25, 'y': 1}, {'x': 26, 'y': 2}, \
                              {'x': 27, 'y': 4}, {'x': 27, 'y': 6}, {'x': 27, 'y': 8}, {'x': 27, 'y': 9}, \
                              {'x': 27, 'y': 11}, {'x': 27, 'y': 12}, {'x': 26, 'y': 13}, \
                              {'x': 25, 'y': 14}, {'x': 24, 'y': 14}, {'x': 22, 'y': 14}, {'x': 21, 'y': 14}, \
                              {'x': 24, 'y': 15}, {'x': 25, 'y': 16}, {'x': 26, 'y': 17}, \
                              {'x': 27, 'y': 18}, {'x': 27, 'y': 19}, {'x': 27, 'y': 21}, {'x': 27, 'y': 22}, \
                              {'x': 27, 'y': 24}, {'x': 27, 'y': 25}, {'x': 27, 'y': 26}, \
                              {'x': 26, 'y': 27}, {'x': 25, 'y': 28}, {'x': 24, 'y': 28}, {'x': 23, 'y': 29}, \
                              {'x': 22, 'y': 29}, {'x': 21, 'y': 29}, {'x': 20, 'y': 29}, \
                              {'x': 32, 'y': 0}, {'x': 33, 'y': 0}, {'x': 34, 'y': 0}, {'x': 35, 'y': 0}, \
                              {'x': 29, 'y': 3}, {'x': 29, 'y': 4}, {'x': 29, 'y': 6}, \
                              {'x': 29, 'y': 7}, {'x': 29, 'y': 8}, {'x': 29, 'y': 10}, {'x': 29, 'y': 11}, \
                              {'x': 29, 'y': 12}, {'x': 29, 'y': 14}, {'x': 29, 'y': 16}, \
                              {'x': 29, 'y': 17}, {'x': 29, 'y': 18}, {'x': 29, 'y': 20}, {'x': 29, 'y': 21}, \
                              {'x': 29, 'y': 23}, {'x': 29, 'y': 25}, {'x': 29, 'y': 26}, \
                              {'x': 30, 'y': 27}, {'x': 31, 'y': 28}, {'x': 32, 'y': 29}, {'x': 33, 'y': 29}, \
                              {'x': 35, 'y': 29}, {'x': 36, 'y': 1}, {'x': 37, 'y': 2}, \
                              {'x': 37, 'y': 3}, {'x': 37, 'y': 5}, {'x': 37, 'y': 7}, {'x': 37, 'y': 8}, \
                              {'x': 37, 'y': 10}, {'x': 37, 'y': 11}, {'x': 31, 'y': 0}, \
                              {'x': 30, 'y': 1}, {'x': 29, 'y': 2}, {'x': 37, 'y': 12}, {'x': 37, 'y': 13}, \
                              {'x': 37, 'y': 14}, {'x': 37, 'y': 15}, {'x': 37, 'y': 16}, \
                              {'x': 37, 'y': 18}, {'x': 37, 'y': 20}, {'x': 37, 'y': 21}, {'x': 37, 'y': 22}, \
                              {'x': 37, 'y': 26}, {'x': 37, 'y': 27}, \
                              {'x': 36, 'y': 28}, {'x': 37, 'y': 25}, {'x': 37, 'y': 23}, {'x': 38, 'y': 0}, \
                              {'x': 39, 'y': 0}, {'x': 40, 'y': 0}, {'x': 42, 'y': 0}, \
                              {'x': 43, 'y': 0}, {'x': 44, 'y': 0}, {'x': 41, 'y': 0}, {'x': 41, 'y': 1}, \
                              {'x': 41, 'y': 2}, {'x': 41, 'y': 4}, {'x': 41, 'y': 5}, \
                              {'x': 41, 'y': 6}, {'x': 41, 'y': 7}, {'x': 41, 'y': 9}, {'x': 41, 'y': 10}, \
                              {'x': 41, 'y': 11}, {'x': 41, 'y': 12}, {'x': 41, 'y': 15}, \
                              {'x': 41, 'y': 13}, {'x': 41, 'y': 14}, {'x': 41, 'y': 16}, {'x': 41, 'y': 18}, \
                              {'x': 41, 'y': 19}, {'x': 41, 'y': 20}, \
                              {'x': 41, 'y': 21}, {'x': 41, 'y': 23}, {'x': 41, 'y': 25}, {'x': 41, 'y': 26}, \
                              {'x': 41, 'y': 27}, {'x': 41, 'y': 29}, {'x': 41, 'y': 28}]

                for coord in wallCoords:
                    x = coord['x'] * CELLSIZE
                    y = coord['y'] * CELLSIZE
                    drawwall(x, y)
                    revealedBoxes[coord['x']][coord['y']] = True

     #鼠标光标指在方格上
    if boxx != None and boxy != None:
        drawHighlightBox(boxx, boxy)
        #如果此方格上没有障碍物，点击鼠标绘制障碍物
        if not revealedBoxes[boxx][boxy] and mouseClicked:
            wallCoords.append({'x': boxx, 'y': boxy})
            for coord in wallCoords:
                x = coord['x'] * CELLSIZE
                y = coord['y'] * CELLSIZE
                drawwall(x, y)
            revealedBoxes[boxx][boxy] = True
        #如果此方格上已有障碍物，点击鼠标清除障碍物
        elif revealedBoxes[boxx][boxy] and mouseClicked:
            wallCoords.remove({'x': boxx, 'y': boxy})
            revealedBoxes[boxx][boxy] = False
            for coord in wallCoords:
                x = coord['x'] * CELLSIZE
                y = coord['y'] * CELLSIZE
                drawwall(x, y)


    #显示窗口
    pygame.display.update()
    FPSCLOCK.tick(FPS)

